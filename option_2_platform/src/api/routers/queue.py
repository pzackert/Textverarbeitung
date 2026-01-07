import logging
import threading
import time
from datetime import datetime, timezone
from typing import Dict, List, Optional

from fastapi import APIRouter, HTTPException

from src.api.dependencies import get_llm_chain, get_ingestion_pipeline, get_config
from src.services.project_service import project_service
from src.services.criteria_service import criteria_service
from src.services.validation_service import validation_service
from src.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/queue", tags=["queue"])

# In-memory queue and worker
_jobs: List[Dict] = []
_job_lock = threading.Lock()
_worker_thread: Optional[threading.Thread] = None
_worker_running = False


def _enqueue(job: Dict) -> Dict:
    with _job_lock:
        for existing in _jobs:
            if existing.get("project_id") != job.get("project_id"):
                continue
            if set(existing.get("criteria_ids", [])) == set(job.get("criteria_ids", [])) and existing.get("status") in {"pending", "running"}:
                # Flag duplicate instead of enqueuing a second job
                dup = dict(existing)
                dup["duplicate"] = True
                return dup
        _jobs.append(job)
    _start_worker()
    return job


def _start_worker():
    global _worker_thread, _worker_running
    if _worker_running:
        return
    _worker_running = True
    _worker_thread = threading.Thread(target=_worker_loop, daemon=True)
    _worker_thread.start()


def _next_job() -> Optional[Dict]:
    with _job_lock:
        for job in _jobs:
            if job.get("status") == "pending":
                job["status"] = "running"
                job["started_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
                return job
    return None


def _worker_loop():
    global _worker_running
    while True:
        job = _next_job()
        if not job:
            _worker_running = False
            return
        try:
            _process_job(job)
            job["status"] = "done"
            job["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        except Exception as exc:
            logger.exception("Queue job failed")
            job["status"] = "failed"
            job["message"] = str(exc)
            job["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        time.sleep(0.01)


def _load_project_into_rag(project_id: str):
    """Clear previous project chunks and ingest uploads for the target project."""
    config = get_config()
    store = VectorStore(
        collection_name=config.collection_name,
        persist_directory=config.persist_directory,
        embedding_function=None,
    )
    # RAG isolation: remove other project chunks, then clear current project to reload
    store.delete_projects_except(project_id)
    store.delete_project(project_id)

    pipeline = get_ingestion_pipeline()
    project = project_service.get_project(project_id)
    if not project:
        raise ValueError(f"Projekt {project_id} nicht gefunden")
    if not project.documents:
        raise ValueError(f"Keine Uploads für Projekt {project_id}")
    for doc in project.documents:
        pipeline.ingest_file(doc.path, project_id=project_id, extra_metadata={"project_id": project_id, "document": doc.filename})


def _process_job(job: Dict):
    project_id = job["project_id"]
    crit_ids = job["criteria_ids"]
    _load_project_into_rag(project_id)
    llm_chain = get_llm_chain()

    job["progress"] = {
        "completed": 0,
        "total": len(crit_ids),
        "results": []
    }

    for idx, cid in enumerate(crit_ids):
        job["current"] = cid
        res = validation_service.evaluate_criterion(project_id, cid, llm_chain=llm_chain)
        
        result_entry = {
            "criterion_id": cid,
            "status": res.get("status"),
        }
        job["results"].append(result_entry)
        
        job["progress"]["results"] = job["results"] # Link for polling
        job["progress"]["completed"] = idx + 1
        
@router.get("/{job_id}")
async def get_job_status(job_id: str):
    with _job_lock:
        for job in _jobs:
            if job["job_id"] == job_id:
                return job
    raise HTTPException(status_code=404, detail="Job nicht gefunden")


@router.post("/projects/{project_id}/criteria/{criterion_id}")
async def enqueue_single(project_id: str, criterion_id: str):
    if not project_service.get_project(project_id):
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    if not criteria_service.get_by_id(criterion_id):
        raise HTTPException(status_code=404, detail="Kriterium nicht gefunden")
    job = {
        "job_id": f"job_{int(time.time()*1000)}",
        "project_id": project_id,
        "criteria_ids": [criterion_id],
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return _enqueue(job)


@router.post("/projects/{project_id}/criteria/all")
async def enqueue_all_for_project(project_id: str):
    if not project_service.get_project(project_id):
        raise HTTPException(status_code=404, detail="Projekt nicht gefunden")
    crit_ids = [c.id for c in criteria_service.get_all()]
    job = {
        "job_id": f"job_{int(time.time()*1000)}",
        "project_id": project_id,
        "criteria_ids": crit_ids,
        "status": "pending",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    }
    return _enqueue(job)


@router.post("/projects/all/criteria/all")
async def enqueue_all_projects_all_criteria():
    jobs_created = []
    crit_ids = [c.id for c in criteria_service.get_all()]
    for project in project_service.list_projects():
        job = {
            "job_id": f"job_{project.id}_{int(time.time()*1000)}",
            "project_id": project.id,
            "criteria_ids": crit_ids,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        }
        jobs_created.append(_enqueue(job))
    return {"jobs": jobs_created}


@router.get("")
async def list_jobs():
    with _job_lock:
        return {"jobs": _jobs}
