from fastapi import APIRouter, Request, HTTPException, Depends, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from backend.services.project_service import ProjectService
from backend.dependencies import get_project_service
from typing import Optional

router = APIRouter(prefix="/projects", tags=["projects"])
templates = Jinja2Templates(directory="frontend/templates")

@router.post("", response_class=HTMLResponse)
async def create_project(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    project_service: ProjectService = Depends(get_project_service)
):
    project_service.create_project(name=name, description=description)
    # For MVP, redirect back to dashboard to see the new list
    return RedirectResponse(url="/", status_code=303)

@router.get("/{project_id}")
async def project_detail(
    request: Request, 
    project_id: str,
    project_service: ProjectService = Depends(get_project_service)
):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return templates.TemplateResponse("project_detail.html", {
        "request": request,
        "project": project,
        # "criteria": CRITERIA # TODO: Add criteria later
    })
