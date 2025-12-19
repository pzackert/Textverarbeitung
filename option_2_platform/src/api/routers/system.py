import logging
from fastapi import APIRouter, Depends, BackgroundTasks
from src.api.schemas import SystemStatus
from src.services.system_state import system_state, run_startup_sequence

router = APIRouter(prefix="/system", tags=["system"])
logger = logging.getLogger(__name__)

@router.post("/startup")
async def startup_system(background_tasks: BackgroundTasks):
    """
    Trigger the system startup sequence in background.
    """
    # Only start if not already running or ready
    if system_state.global_status == "ready":
         logger.info("System already ready, skipping startup sequence.")
         return {"message": "System already ready", "status": "ready"}
    
    # If initializing/pending, we allow it to run (idempotent-ish)
    # This prevents the deadlock where default state is "initializing" but task never started.
    
    background_tasks.add_task(run_startup_sequence)
    return {"message": "Startup initiated", "status": "initializing"}

    background_tasks.add_task(run_startup_sequence)
    return {"message": "Startup initiated", "status": "initializing"}

@router.get("/status", response_model=SystemStatus)
async def get_system_status():
    """
    Get the granular status of all system components.
    """
    return system_state.get_status_dict()

@router.get("/health")
async def health_check():
    """
    Simple health check for Docker/K8s.
    Returns 200 if API is up, regardless of internal component state.
    """
    return {"status": "ok"}
