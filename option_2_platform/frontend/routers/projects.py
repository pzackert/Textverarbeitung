from fastapi import APIRouter, Request, HTTPException, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from typing import Optional
from pathlib import Path
import logging
from src.services.project_service import project_service
from src.services.validation_service import ValidationService
from frontend.services.api_client import api_client
import os

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])
templates = Jinja2Templates(directory="frontend/templates")

def get_status_display(status: str) -> str:
    mapping = {
        "draft": "Entwurf",
        "in_review": "In Prüfung",
        "completed": "Abgeschlossen",
        "archived": "Archiviert"
    }
    return mapping.get(status, status)

@router.get("", response_class=HTMLResponse)
async def projects_overview(
    request: Request,
    search: Optional[str] = None,
    status_filter: Optional[str] = None
):
    """Antrags-Übersicht - Liste aller Projekte."""
    projects = project_service.list_projects()
    
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
    
    # Statistiken pro Projekt
    for project in filtered_projects:
        project.doc_count = len(project.documents)
        project.status_display = get_status_display(project.status)
        project.last_updated = project.updated_at.strftime("%d.%m.%Y")
    
    # Check if HTMX request for table update
    if request.headers.get("HX-Request") and request.headers.get("HX-Target") == "projects-table-body":
        return templates.TemplateResponse(
            request=request,
            name="partials/projects_table_rows.html",
            context={"projects": filtered_projects}
        )
    
    return templates.TemplateResponse(
        request=request,
        name="projects_overview.html",
        context={"projects": filtered_projects, "current_page": "projects"}
    )

@router.post("", response_class=HTMLResponse)
async def create_project(
    request: Request,
    name: str = Form(...),
    description: Optional[str] = Form(None),
    applicant: Optional[str] = Form(None),
    funding_amount: Optional[float] = Form(None)
):
    project_service.create_project(
        name=name, 
        description=description,
        applicant=applicant,
        funding_amount=funding_amount
    )
    # Redirect to projects list
    return RedirectResponse(url="/projects", status_code=303)

@router.delete("/{project_id}")
async def delete_project(project_id: str):
    success = project_service.delete_project(project_id)
    if not success:
        raise HTTPException(404, "Project not found")
    return HTMLResponse("")

@router.get("/{project_id}/review", response_class=HTMLResponse)
async def project_review(project_id: str, request: Request):
    """Smart Review Cockpit für einen Antrag."""
    project = project_service.get_project(project_id)
    
    if not project:
        raise HTTPException(404, "Projekt nicht gefunden")
    
    # Prepare project display fields
    project.status_display = get_status_display(project.status)
    
    return templates.TemplateResponse(
        request=request,
        name="project_review.html",
        context={"project": project, "current_page": "projects"}
    )

@router.post("/{project_id}/validate")
async def validate_project(
    project_id: str, 
    request: Request,
    background_tasks: BackgroundTasks
):
    """Trigger validation for a project."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    async def run_validation():
        try:
            service = ValidationService()
            result = await service.validate_project(project)
            
            # Update project with results
            project.validation_results = result
            project.annotated_documents = result.get("annotated_documents", {})
            project_service.update_project(project)
            
            logger.info(f"Validation completed for {project_id}")
        except Exception as e:
            logger.error(f"Validation failed: {e}")
    
    background_tasks.add_task(run_validation)
    
    return templates.TemplateResponse(
        "partials/validation_progress.html",
        {
            "request": request,
            "project_id": project_id,
            "status": "in_progress"
        }
    )

@router.get("/{project_id}/validation-status")
async def validation_status(project_id: str, request: Request):
    """Check validation status."""
    project = project_service.get_project(project_id)
    if not project:
        return templates.TemplateResponse(
            "partials/validation_progress.html",
            {"request": request, "project_id": project_id}
        )
        
    if project.validation_results:
        return templates.TemplateResponse(
            "partials/validation_results.html",
            {
                "request": request,
                "project": project,
                "results": project.validation_results
            }
        )
    else:
        return templates.TemplateResponse(
            "partials/validation_progress.html",
            {
                "request": request,
                "project_id": project_id,
                "status": "in_progress"
            }
        )

@router.get("/{project_id}/files/{filename}")
async def get_project_file(project_id: str, filename: str):
    """Serves a raw file from the project directory."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
        
    # Check if it's an annotated file
    is_annotated = filename.startswith("annotated_")
    original_filename = filename.replace("annotated_", "") if is_annotated else filename
    
    # Find document by filename
    target_doc = next((d for d in project.documents if d.filename == original_filename), None)
    
    if target_doc:
        if is_annotated:
            # Construct path for annotated file
            # Try same directory as original file first
            p = Path(target_doc.path)
            file_path = str(p.parent / filename)
            
            # If not found there, check if it's in the new input structure
            if not os.path.exists(file_path):
                 file_path = f"data/input/{project_id}/{filename}"
        else:
            file_path = target_doc.path
    else:
        # Fallback for demo/testing
        if filename == "dummy.pdf":
             file_path = "data/input/dummy.pdf"
        else:
             # User requested path: data/input/<project_id>
             file_path = f"data/input/{project_id}/{filename}"

    if not os.path.exists(file_path):
        # Try legacy path just in case
        legacy_path = f"data/projects/{project_id}/{filename}"
        if os.path.exists(legacy_path):
            file_path = legacy_path
        else:
            # Try new input path
            new_path = f"data/input/{project_id}/{filename}"
            if os.path.exists(new_path):
                file_path = new_path
            else:
                raise HTTPException(404, "File not found")
        
    return FileResponse(file_path)

@router.post("/{project_id}/analyze", response_class=HTMLResponse)
async def analyze_project(project_id: str, request: Request):
    """Startet die Analyse und gibt die Ergebnisse zurück (State 2)."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
        
    # Mock Analysis Results with Citations
    # In a real app, this would come from the RAG system
    
    # Find the PDF document ID for citations
    pdf_doc = next((d for d in project.documents if d.filename.endswith('.pdf')), None)
    pdf_doc_id = pdf_doc.id if pdf_doc else "unknown"
    pdf_filename = pdf_doc.filename if pdf_doc else "Dokument.pdf"

    criteria_results = [
        {
            "id": "K001",
            "name": "Betriebsstätte Hamburg",
            "status": "pass",
            "answer": "Ja, erfüllt",
            "reasoning": "Der Antragsteller hat eine registrierte Betriebsstätte in Hamburg gemäß Gewerbeanmeldung. Der Mietvertrag bestätigt die Adresse in Altona.",
            "citations": [
                {
                    "doc_id": pdf_doc_id,
                    "doc_name": pdf_filename,
                    "page": 1,
                    "text_snippet": "Hamburg"
                }
            ]
        },
        {
            "id": "K002",
            "name": "KMU-Status",
            "status": "pass",
            "answer": "Ja, erfüllt",
            "reasoning": "Die Mitarbeiterzahl liegt unter 250 (aktuell 45) und der Jahresumsatz unter 50 Mio. EUR.",
            "citations": [
                {
                    "doc_id": pdf_doc_id,
                    "doc_name": pdf_filename,
                    "page": 2,
                    "text_snippet": "Mitarbeiter"
                }
            ]
        },
        {
            "id": "K003",
            "name": "Innovationsgehalt",
            "status": "warning",
            "answer": "Prüfung erforderlich",
            "reasoning": "Der technische Innovationsgrad ist im Projektplan beschrieben, aber die Abgrenzung zum Stand der Technik ist nicht eindeutig formuliert.",
            "citations": [
                {
                    "doc_id": pdf_doc_id,
                    "doc_name": pdf_filename,
                    "page": 3,
                    "text_snippet": "Innovation"
                }
            ]
        }
    ]

    return templates.TemplateResponse(
        request=request,
        name="components/validation_results.html",
        context={"project": project, "criteria_results": criteria_results}
    )

@router.get("/{project_id}/view/{doc_id}", response_class=HTMLResponse)
async def view_document(project_id: str, doc_id: str, request: Request):
    """Returns the viewer content for a specific document (SPA update)."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
    
    doc = next((d for d in project.documents if d.id == doc_id), None)
    if not doc:
        raise HTTPException(404, "Document not found")
        
    return templates.TemplateResponse(
        request=request,
        name="partials/viewer_content.html",
        context={"project": project, "doc": doc}
    )

@router.post("/{project_id}/status", response_class=HTMLResponse)
async def update_project_status(project_id: str, request: Request, status: str = Form(...)):
    """Updates project status and returns the updated status card."""
    project = project_service.update_project_status(project_id, status)
    if not project:
        raise HTTPException(404, "Project not found")
        
    # Return just the status card HTML (or re-render a partial)
    # For simplicity, we might need a partial for the status card.
    # Here we just return a success indicator or the full card if we extract it.
    # Let's assume we extract the status card to a partial.
    return templates.TemplateResponse(
        request=request,
        name="partials/project_status_card.html",
        context={"project": project}
    )

@router.post("/{project_id}/chat", response_class=HTMLResponse)
async def chat_project(project_id: str, request: Request, message: str = Form(...)):
    """Chat mit dem KI-Assistenten."""
    # In a real app, we would call the LLM here.
    # For now, we return a dummy response.
    
    # Render User Message
    user_msg_html = templates.get_template("partials/chat_message.html").render(
        role="user", message=message
    )
    
    # Render Assistant Message
    # Simple logic for demo purposes
    if "finanz" in message.lower():
        response_text = "Der Finanzplan sieht solide aus. Die Personalkosten liegen im üblichen Rahmen (65% des Budgets)."
    elif "kmu" in message.lower():
        response_text = "Das Unternehmen erfüllt die KMU-Kriterien: < 250 Mitarbeiter und < 50 Mio. € Umsatz."
    else:
        response_text = f"Das ist eine interessante Frage zu '{message}'. Ich analysiere die Dokumente..."

    assistant_msg_html = templates.get_template("partials/chat_message.html").render(
        role="assistant", message=response_text
    )
    
    return HTMLResponse(content=user_msg_html + assistant_msg_html)

@router.post("/{project_id}/upload", response_class=HTMLResponse)
async def upload_document(project_id: str, request: Request, file: UploadFile = File(...)):
    """Uploads a document to the project."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
        
    # Save file
    try:
        content = await file.read()
        filename = file.filename or "uploaded_file"
        doc = project_service.save_document(project_id, filename, content)
    except Exception as e:
        # Handle error (e.g. file save failed)
        print(f"Upload error: {e}")
        pass
    
    # Redirect back to review
    return RedirectResponse(url=f"/projects/{project_id}/review", status_code=303)

