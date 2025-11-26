from pathlib import Path
from functools import lru_cache
from backend.services.project_service import ProjectService

# Define where data is stored
DATA_DIR = Path("data/projects")

@lru_cache()
def get_project_service() -> ProjectService:
    return ProjectService(storage_root=DATA_DIR)
