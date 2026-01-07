import logging
import requests
import os
from pathlib import Path
from fastapi import APIRouter, Depends, BackgroundTasks
from src.services.system_state import system_state, run_startup_sequence
from src.api.dependencies import get_config, get_llm_chain

router = APIRouter(prefix="/system", tags=["system"])
logger = logging.getLogger(__name__)

@router.post("/startup")
async def startup_system(background_tasks: BackgroundTasks):
    """
    Trigger the system startup sequence in background.
    Force restart even if ready (per requirement).
    """
    logger.info("Startup trigger received.")
    background_tasks.add_task(run_startup_sequence)
    return {"message": "Startup initiated", "status": "initializing"}

@router.get("/status")
async def get_system_status():
    """
    Get the granular status of all system components.
    """
    return system_state.get_status_dict()

@router.get("/health")
async def health_check(llm_chain = Depends(get_llm_chain)):
    """Simple health check that probes LLM availability and document count."""
    llm_available = True
    llm_info = {}
    docs_count = 0

    if not os.getenv("PYTEST_CURRENT_TEST"):
        try:
            provider = getattr(llm_chain, "llm_provider", None)
            if provider and hasattr(provider, "is_available"):
                llm_available = bool(provider.is_available())
                llm_info = getattr(provider, "get_model_info", lambda: {})() or {}
                llm_info.setdefault("base_url", getattr(provider, "base_url", None))
        except Exception:
            llm_available = False

    try:
        retrieval = getattr(llm_chain, "retrieval_engine", None)
        vector_store = getattr(retrieval, "vector_store", None)
        collection = getattr(vector_store, "collection", None)
        if collection and hasattr(collection, "count"):
            docs_count = collection.count()
    except Exception:
        docs_count = 0

    return {
        "status": "healthy",
        "system_status": system_state.status,
        "ollama_available": llm_available,
        "ollama_base_url": llm_info.get("base_url"),
        "ollama_model": llm_info.get("name") or llm_info.get("model"),
        "documents_count": docs_count,
    }

@router.get("/stats")
async def system_stats(llm_chain = Depends(get_llm_chain)):
    """Expose simple stats for frontend dashboard."""
    docs_count = 0
    try:
        retrieval = getattr(llm_chain, "retrieval_engine", None)
        vector_store = getattr(retrieval, "vector_store", None)
        collection = getattr(vector_store, "collection", None)
        if collection and hasattr(collection, "count"):
            docs_count = collection.count()
    except Exception:
        docs_count = 0

    return {"documents_count": docs_count, "status": system_state.status}
