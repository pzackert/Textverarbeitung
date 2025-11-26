from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from frontend.mock_data import PROJECTS, CRITERIA

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/antraege")
async def list_projects(request: Request):
    return templates.TemplateResponse("projects_list.html", {
        "request": request,
        "projects": PROJECTS
    })

@router.get("/antrag/{project_id}")
async def project_detail(request: Request, project_id: str):
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return templates.TemplateResponse("project_detail.html", {
        "request": request,
        "project": project,
        "criteria": CRITERIA
    })
