from fastapi import APIRouter, Request, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from frontend.services.project_service import project_service
from frontend.services.api_client import api_client

router = APIRouter(prefix="/projects", tags=["projects"])
templates = Jinja2Templates(directory="frontend/templates")

@router.get("", response_class=HTMLResponse)
async def list_projects(request: Request):
    """List all projects."""
    # For now, the dashboard is the main project list view
    return RedirectResponse(url="/")

@router.post("", response_class=HTMLResponse)
async def create_project(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None)
):
    project_service.create_project(name=name, description=description)
    # For MVP, redirect back to dashboard to see the new list
    return RedirectResponse(url="/", status_code=303)

@router.get("/{project_id}")
async def project_detail(
    request: Request, 
    project_id: str
):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    return templates.TemplateResponse(
        request=request,
        name="project_detail.html",
        context={
            "project": project,
        }
    )

@router.post("/{project_id}/upload", response_class=HTMLResponse)
async def upload_document(
    request: Request,
    project_id: str,
    file: UploadFile = File(...)
):
    try:
        # 1. Save locally first (legacy project requirement)
        content = await file.read()
        file_path = project_service.save_document(project_id, file.filename, content)
        
        # 2. Trigger RAG Ingestion via API
        response = await api_client.upload_document(file_path)
        chunks_count = response.get("chunks_count", 0)
        
        # 3. Return Success Feedback
        return HTMLResponse(f"""
            <div class="p-4 mb-4 text-sm text-green-800 rounded-lg bg-green-50" role="alert">
                <span class="font-medium">Success!</span> Document processed. {chunks_count} chunks created.
            </div>
        """)
        
    except Exception as e:
        # 4. Return Error Feedback
        return HTMLResponse(f"""
            <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50" role="alert">
                <span class="font-medium">Error!</span> Processing failed: {str(e)}
            </div>
        """)
