from fastapi import APIRouter, Request, HTTPException, Form, UploadFile, File
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from backend import projekt_manager

router = APIRouter(prefix="/projects", tags=["projects"])
templates = Jinja2Templates(directory="option_1_mvp/frontend/templates")

# Pydantic Models for better typing in templates
class Project(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    applicant: Optional[str] = None
    funding_amount: Optional[float] = None
    status: str = "draft"
    created_at: str
    updated_at: str
    documents: List[dict] = []
    
    # Helper properties for template
    @property
    def status_display(self) -> str:
        mapping = {
            "draft": "Entwurf",
            "in_review": "In Prüfung",
            "completed": "Abgeschlossen",
            "archived": "Archiviert"
        }
        return mapping.get(self.status, self.status)

    @property
    def doc_count(self) -> int:
        return len(self.documents)
        
    @property
    def last_updated(self) -> str:
        try:
            dt = datetime.fromisoformat(self.updated_at)
            return dt.strftime("%d.%m.%Y")
        except:
            return self.updated_at

def map_to_project(data: dict) -> Project:
    return Project(
        id=data.get("projekt_id", ""),
        name=data.get("projekt_name", ""),
        description=data.get("beschreibung"),
        applicant=data.get("antragsteller"),
        funding_amount=data.get("funding_amount"), # Assuming this field exists or will be added
        status=data.get("status", "draft"),
        created_at=data.get("created_at", ""),
        updated_at=data.get("updated_at", ""),
        documents=data.get("documents", [])
    )

@router.get("", response_class=HTMLResponse)
async def projects_overview(
    request: Request,
    search: Optional[str] = None,
    status_filter: Optional[str] = None
):
    """Antrags-Übersicht - Liste aller Projekte."""
    raw_projects = projekt_manager.list_projects()
    projects = [map_to_project(p) for p in raw_projects]
    
    # Filter logic
    filtered_projects = []
    for p in projects:
        # Status Filter
        if status_filter and status_filter != "all":
            if p.status != status_filter:
                continue
        
        # Search Filter
        if search:
            search_lower = search.lower()
            if (search_lower not in p.name.lower() and 
                search_lower not in (p.applicant or "").lower()):
                continue
                
        filtered_projects.append(p)
    
    # Check if HTMX request for table update
    if request.headers.get("HX-Request") and request.headers.get("HX-Target") == ".projects-table":
        return templates.TemplateResponse(
            request=request,
            name="partials/projects_table_rows.html",
            context={"projects": filtered_projects}
        )
    
    return templates.TemplateResponse(
        request=request,
        name="projects_overview.html",
        context={"projects": filtered_projects}
    )

@router.post("", response_class=HTMLResponse)
async def create_project(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    applicant: Optional[str] = Form(None),
    funding_amount: Optional[float] = Form(None)
):
    # Using projekt_manager.create_projekt
    # Note: create_projekt signature might need adjustment or we map fields
    projekt_manager.create_projekt(
        projekt_name=name,
        antragsteller=applicant or "Unbekannt",
        modul="Standard", # Default
        projektart="Standard", # Default
        beschreibung=description
    )
    # Note: funding_amount is not in create_projekt yet, would need to be added to metadata update if needed
    
    # Redirect to projects list
    return RedirectResponse(url="/projects", status_code=303)

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    success = projekt_manager.delete_projekt(project_id)
    if not success:
        raise HTTPException(404, "Project not found")
    return HTMLResponse("")

@router.get("/{project_id}/review", response_class=HTMLResponse)
async def project_review(project_id: str, request: Request):
    """Smart Review Cockpit für einen Antrag."""
    try:
        data = projekt_manager.load_projekt_metadata(project_id)
        project = map_to_project(data)
    except FileNotFoundError:
        raise HTTPException(404, "Projekt nicht gefunden")
    
    # Lade Dokumente mit Status (Mock status for now)
    documents = []
    for doc in project.documents:
        # Mocking document info for now as per prompt logic
        # Assuming doc is a dict or string path in the metadata
        doc_name = doc.get("name", "Unbekannt") if isinstance(doc, dict) else str(doc)
        doc_path = doc.get("path", "") if isinstance(doc, dict) else str(doc)
        
        doc_info = {
            "id": doc.get("id", "0"), # Mock ID
            "name": doc_name,
            "type": doc_name.split('.')[-1].lower(),
            "pages": "?", # Placeholder
            "status": "ready", # Placeholder
            "path": doc_path
        }
        documents.append(doc_info)
    
    # Erste Dokument als aktiv markieren
    active_doc = documents[0] if documents else None
    
    return templates.TemplateResponse(
        request=request,
        name="project_review.html",
        context={
            "project": project,
            "documents": documents,
            "active_doc": active_doc
        }
    )

@router.post("/{project_id}/upload", response_class=HTMLResponse)
async def upload_document(
    request: Request,
    project_id: str,
    file: UploadFile = File(...)
):
    try:
        # 1. Save locally first
        # We need to implement save_document in projekt_manager or do it here
        # For now, let's do it here using projekt_manager paths
        from pathlib import Path
        import shutil
        
        project_path = Path(f"data/projects/{project_id}")
        if not project_path.exists():
             raise HTTPException(404, "Project not found")
             
        upload_dir = project_path / "uploads"
        upload_dir.mkdir(exist_ok=True)
        
        file_path = upload_dir / file.filename
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Update metadata
        data = projekt_manager.load_projekt_metadata(project_id)
        new_doc = {"name": file.filename, "path": str(file_path), "id": str(len(data.get("documents", [])) + 1)}
        data.setdefault("documents", []).append(new_doc)
        projekt_manager.update_projekt_metadata(project_id, {"documents": data["documents"]})
        
        # Return new doc item for the list
        doc_info = {
            "id": new_doc["id"],
            "name": new_doc["name"],
            "type": new_doc["name"].split('.')[-1].lower(),
            "pages": "?",
            "status": "ready",
            "path": new_doc["path"]
        }
        
        return templates.TemplateResponse(
            request=request,
            name="partials/doc_item.html",
            context={"doc": doc_info, "project": {"id": project_id}, "active_doc": doc_info}
        )
        
    except Exception as e:
        return HTMLResponse(f"Error: {str(e)}", status_code=500)

@router.post("/{project_id}/status")
async def update_status(project_id: str, status: str = Form(...)):
    projekt_manager.update_projekt_metadata(project_id, {"status": status})
    return HTMLResponse("")
