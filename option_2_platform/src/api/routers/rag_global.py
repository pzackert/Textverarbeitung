import logging
import time
import uuid
from pathlib import Path
from typing import Dict, Any

from fastapi import APIRouter, BackgroundTasks, HTTPException, status

from src.api.dependencies import get_ingestion_pipeline, get_config
from src.rag.vector_store import VectorStore

router = APIRouter(prefix="/rag/global", tags=["rag_global"])
logger = logging.getLogger(__name__)

# Job state held in-memory for polling
rag_job: Dict[str, Any] = {
    "status": "unloaded",
    "job_id": None,
    "documents": [],
    "total_chunks": 0,
    "overall_progress_pct": 0,
    "total_load_time_sec": 0.0,
}


def _reset_job(documents: list):
    rag_job.update({
        "status": "loading",
        "job_id": f"rag_load_{time.strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}",
        "documents": [
            {
                "filename": d.name,
                "status": "pending",
                "progress_pct": 0,
                "chunks_created": 0,
                "parse_time_sec": None,
                "error": None,
            }
            for d in documents
        ],
        "overall_progress_pct": 0,
        "total_chunks": 0,
        "total_load_time_sec": 0.0,
    })


def _update_doc(filename: str, **kwargs):
    for doc in rag_job.get("documents", []):
        if doc.get("filename") == filename:
            doc.update(kwargs)
            break


def _compute_progress():
    docs = rag_job.get("documents", [])
    if not docs:
        return 0
    return int(sum(d.get("progress_pct", 0) for d in docs) / len(docs))


def _run_load_job(doc_paths, pipeline):
    start = time.perf_counter()
    total_chunks = 0
    for path in doc_paths:
        t0 = time.perf_counter()
        _update_doc(path.name, status="loading", progress_pct=5)
        try:
            result = pipeline.ingest_file(
                str(path),
                project_id=None,
                extra_metadata={"type": "global_knowledge", "document": path.name},
            )
            chunks = result.get("chunk_count", 0)
            total_chunks += chunks
            duration = round(time.perf_counter() - t0, 2)
            
            # Incremental update of job state
            rag_job["total_chunks"] = total_chunks
            
            _update_doc(
                path.name,
                status="complete",
                progress_pct=100,
                chunks_created=chunks,
                parse_time_sec=duration,
                error=None,
            )
        except Exception as exc:  # pragma: no cover - runtime guard
            _update_doc(
                path.name,
                status="failed",
                progress_pct=0,
                error=str(exc),
            )
            rag_job["status"] = "error"
            rag_job["overall_progress_pct"] = _compute_progress()
            # Do NOT return, continue to next file
            continue
        rag_job["overall_progress_pct"] = _compute_progress()
    rag_job["status"] = "ready"
    rag_job["total_chunks"] = total_chunks
    rag_job["total_load_time_sec"] = round(time.perf_counter() - start, 2)


def _clean_global_chunks():
    try:
        config = get_config()
        vs = VectorStore(
            collection_name=config.collection_name,
            persist_directory=config.persist_directory,
            embedding_function=None,
        )
        vs.delete_by_metadata({"type": "global_knowledge"})
    except Exception as exc:
        logger.warning(f"Failed to clean global knowledge chunks: {exc}")


@router.post("/load", status_code=status.HTTP_202_ACCEPTED)
async def load_global(background_tasks: BackgroundTasks, force_reload: bool = False):
    data_dir = Path("data/global_knowledge")
    if not data_dir.exists():
        raise HTTPException(status_code=404, detail="global_knowledge directory not found")
    doc_paths = sorted([p for p in data_dir.iterdir() if p.is_file()])
    _reset_job(doc_paths)
    _clean_global_chunks()
    pipeline = get_ingestion_pipeline()
    background_tasks.add_task(_run_load_job, doc_paths, pipeline)
    return {
        "job_id": rag_job["job_id"],
        "status": "started",
        "total_documents": len(doc_paths),
        "documents": [p.name for p in doc_paths],
    }

def start_background_load():
    """Helper to trigger loading from system startup."""
    data_dir = Path("data/global_knowledge")
    if not data_dir.exists():
        return
    doc_paths = sorted([p for p in data_dir.iterdir() if p.is_file()])
    if not doc_paths:
        return
        
    if rag_job.get("status") == "loading":
        logger.info("Global RAG load already in progress, skipping auto-load trigger.")
        return

    logger.info(f"Auto-loading {len(doc_paths)} global documents...")
    _reset_job(doc_paths)
    # Note: We don't clean chunks here to avoid wiping persistence if it was partial.
    # Actually, for auto-load on empty DB, cleaning is fine/noop.
    
    pipeline = get_ingestion_pipeline()
    # Run synchronously in a thread or just call logic? 
    # Since this is called from asyncio.create_task in main, we can just run it.
    # But _run_load_job is synchronous blocking IO.
    # We should run it in a separate thread/task.
    
    import threading
    t = threading.Thread(target=_run_load_job, args=(doc_paths, pipeline))
    t.start()


@router.get("/status")
async def get_status():
    rag_job["overall_progress_pct"] = _compute_progress()
    return rag_job


@router.post("/unload")
async def unload_global():
    _clean_global_chunks()
    chunks_removed = rag_job.get("total_chunks", 0)
    rag_job.update({
        "status": "unloaded",
        "overall_progress_pct": 0,
        "total_chunks": 0,
        "documents": [],
    })
    return {
        "status": "unloaded",
        "chunks_removed": chunks_removed,
        "duration_sec": 0.0,
    }
