from fastapi import APIRouter, Request, HTTPException, Depends, Form, UploadFile, File
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
    
    return templates.TemplateResponse(
        request=request,
        name="project_detail.html",
        context={
            "project": project,
            # "criteria": CRITERIA # TODO: Add criteria later
        }
    )

@router.post("/{project_id}/upload", response_class=HTMLResponse)
async def upload_document(
    request: Request,
    project_id: str,
    file: UploadFile = File(...),
    project_service: ProjectService = Depends(get_project_service)
):
    content = await file.read()
    project_service.save_document(project_id, file.filename, content)
    
    # Reload project to get updated documents list
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    return templates.TemplateResponse(
        request=request,
        name="partials/document_list.html",
        context={
            "project": project
        }
    )
