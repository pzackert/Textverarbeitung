from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from frontend.mock_data import PROJECTS

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/")
async def dashboard(request: Request):
    # Calculate stats
    open_projects = len([p for p in PROJECTS if p["status"] != "Abgeschlossen"])
    high_priority = len([p for p in PROJECTS if p["priority"] == "Hoch"])
    completed_week = len([p for p in PROJECTS if p["status"] == "Abgeschlossen"]) # Mock logic

    stats = {
        "open_projects": open_projects,
        "high_priority": high_priority,
        "completed_week": completed_week
    }

    return templates.TemplateResponse("index.html", {
        "request": request,
        "projects": PROJECTS[:5], # Show recent 5
        "stats": stats
    })
