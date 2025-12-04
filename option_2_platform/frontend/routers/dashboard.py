from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from frontend.services.project_service import project_service
from frontend.services.api_client import api_client

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/")
async def dashboard(request: Request):
    projects = project_service.list_projects()
    
    # Get system stats from API
    try:
        system_stats = await api_client.get_system_stats()
        ollama_status = "Running" # We assume running if call succeeds, or check specific field
        chromadb_status = "Connected"
        doc_count = system_stats.get("documents_count", 0)
    except Exception as e:
        system_stats = {}
        ollama_status = "Error"
        chromadb_status = "Error"
        doc_count = 0
    
    stats = {
        "open_projects": len(projects),
        "documents_count": doc_count,
        "ollama_status": ollama_status,
        "chromadb_status": chromadb_status
    }

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "projects": projects,
            "stats": stats
        }
    )
