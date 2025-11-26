from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from backend.services.project_service import ProjectService
from backend.dependencies import get_project_service

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/")
async def dashboard(
    request: Request,
    project_service: ProjectService = Depends(get_project_service)
):
    projects = project_service.list_projects()
    
    # Simple stats for MVP
    stats = {
        "open_projects": len(projects),
        "high_priority": 0, # Placeholder
        "completed_week": 0 # Placeholder
    }

    return templates.TemplateResponse("index.html", {
        "request": request,
        "projects": projects,
        "stats": stats
    })
