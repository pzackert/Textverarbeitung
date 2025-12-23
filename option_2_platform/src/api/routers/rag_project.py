import logging
import os
import time
from typing import Dict, Any, List
from fastapi import APIRouter, HTTPException, status, BackgroundTasks

from src.api.dependencies import get_config
from src.rag.vector_store import VectorStore
from src.rag.ingestion import IngestionPipeline
from src.services.project_service import project_service

router = APIRouter(prefix="/api/rag/project", tags=["rag_project"])
logger = logging.getLogger(__name__)

# In-memory job state: project_id -> { status: str, files: { filename: { status: str, progress: int } } }
rag_jobs: Dict[str, Any] = {}

def _reset_job(project_id: str, documents: List[Any]):
    rag_jobs[project_id] = {
        "status": "loading",
        "progress": 0,
        "files": {
            doc.filename: {
                "status": "pending",
                "progress": 0,
                "error": None
            } for doc in documents
        }
    }

def _update_job_status(project_id: str, status: str, progress: int = None):
    if project_id in rag_jobs:
        rag_jobs[project_id]["status"] = status
        if progress is not None:
             rag_jobs[project_id]["progress"] = progress

def _update_file_status(project_id: str, filename: str, status: str, progress: int = 0, error: str = None):
    if project_id in rag_jobs and filename in rag_jobs[project_id]["files"]:
        rag_jobs[project_id]["files"][filename].update({
            "status": status,
            "progress": progress,
            "error": error
        })

def _run_ingestion_task(project_id: str):
    logger.info(f"Starting background ingestion for project {project_id}")
    project = project_service.get_project(project_id)
    if not project or not project.documents:
        _update_job_status(project_id, "ready", 100)
        return

    try:
        pipeline = IngestionPipeline()
        total_docs = len(project.documents)
        completed = 0

        for i, doc in enumerate(project.documents):
            file_path = doc.path
            # Modern path fallback check
            if not os.path.exists(file_path):
                modern_path = f"data/input/{project_id}/uploads/{doc.filename}"
                if os.path.exists(modern_path):
                    file_path = modern_path
            
            if not os.path.exists(file_path):
                 _update_file_status(project_id, doc.filename, "error", 0, "File not found")
                 continue
            
            _update_file_status(project_id, doc.filename, "loading", 10)
            try:
                # Actual ingestion
                start_t = time.perf_counter()
                pipeline.ingest_file(file_path, project_id=project_id, extra_metadata={"filename": doc.filename})
                
                # Mock progress for UX feeling (optional, but ingestion is sync)
                _update_file_status(project_id, doc.filename, "ready", 100)
                
            except Exception as e:
                logger.error(f"Failed to ingest {doc.filename}: {e}")
                _update_file_status(project_id, doc.filename, "error", 0, str(e))
                # Continue with next file
            
            completed += 1
            overall = int((completed / total_docs) * 100)
            _update_job_status(project_id, "loading", overall)

        _update_job_status(project_id, "ready", 100)
        logger.info(f"Ingestion completed for {project_id}")

    except Exception as e:
        logger.error(f"Critical error in ingestion task for {project_id}: {e}")
        _update_job_status(project_id, "error")


@router.post("/{project_id}/ingest", status_code=status.HTTP_202_ACCEPTED)
async def ingest_project(project_id: str, background_tasks: BackgroundTasks):
    """Start ingestion for a project."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    # Initialize job state
    _reset_job(project_id, project.documents)
    
    # Start background task
    background_tasks.add_task(_run_ingestion_task, project_id)
    
    return {"status": "started", "job": rag_jobs[project_id]}


@router.get("/{project_id}/status")
async def get_ingest_status(project_id: str):
    """Get ingestion status."""
    return rag_jobs.get(project_id, {"status": "unknown"})


@router.post("/{project_id}/unload")
async def unload_project(project_id: str):
    """Remove RAG context and clear job state."""
    try:
        config = get_config()
        store = VectorStore(
            collection_name=config.collection_name,
            persist_directory=config.persist_directory,
            embedding_function=None,
        )
        store.delete_by_metadata({"project_id": project_id})
        
        # Clear job state
        if project_id in rag_jobs:
            del rag_jobs[project_id]
            
        return {"status": "unloaded", "project_id": project_id}
    except Exception as exc:
        logger.error(f"Failed to unload project {project_id}: {exc}")
        raise HTTPException(status_code=500, detail=f"Failed to unload project {project_id}: {exc}")
