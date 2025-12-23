import logging
import requests
from pathlib import Path
from fastapi import APIRouter, Depends, BackgroundTasks
from src.services.system_state import system_state, run_startup_sequence
from src.api.dependencies import get_config

router = APIRouter(prefix="/api/system", tags=["system"])
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
async def health_check():
    """Simple health check that also probes system readiness."""
    return {
        "status": "healthy",
        "system_status": system_state.status
    }
