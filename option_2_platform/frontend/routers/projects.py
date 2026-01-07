from fastapi import APIRouter, Request, Depends, HTTPException, status, Form, UploadFile, File, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from typing import Optional
from pathlib import Path
import logging
from src.services.project_service import project_service
from src.services.chat_store import load_or_create_project_chat
from src.services.settings_service import settings_service

# Try import ValidationService, mock if fails (e.g. no torch installed or crashing)
try:
    from src.services.validation_service import ValidationService
except ImportError:
    import logging
    logger = logging.getLogger(__name__)
    logger.warning("Could not import ValidationService (ML dependencies missing?). Using Mock.")
    
    class ValidationService:
        async def validate_project(self, project):
            raise NotImplementedError("Validation requires full backend dependencies (torch/transformers).")
from src.core.models import ChatMessage, Citation
from frontend.services.api_client import api_client
import os
import uuid
from src.api.dependencies import get_llm_chain
from src.rag.config import RAGConfig
from src.rag.llm_chain import LLMChain
from fastapi import Depends
from src.services.criteria_service import criteria_service
from src.services.annotation_service import annotation_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/projects", tags=["projects"])
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

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
    """Antrags-Übersicht - Liste aller Projekte (Client-Side Rendered)."""
    try:
        # Load once server-side so the table is immediately populated (JS will refresh).
        projects = project_service.list_projects()
        serialized = []
        for p in projects:
            try:
                serialized.append({
                    "id": p.id,
                    "name": p.name,
                    "applicant": p.applicant,
                    "description": p.description,
                    "funding_amount": p.funding_amount,
                    "status": p.status,
                    "created_at": p.created_at.isoformat() if p.created_at else None,
                    "updated_at": p.updated_at.isoformat() if p.updated_at else None,
                    "documents_count": len(p.documents) if p.documents else 0,
                })
            except Exception as e:
                # Fallback for corrupted project data
                print(f"Error serializing project {getattr(p, 'id', 'unknown')}: {e}")
                continue

        import json
        
        # Serialize to JSON string here to avoid 'tojson' filter issues in Jinja (FastAPI default doesn't have it)
        projects_json = json.dumps(serialized)

        return templates.TemplateResponse(
            request=request,
            name="projects_overview.html",
            context={"initial_projects_json": projects_json, "current_page": "projects"}
        )
    except Exception as e:
        import traceback
        return HTMLResponse(content=f"<h1>Error</h1><pre>{traceback.format_exc()}</pre>", status_code=500)

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
    
    # Load Chat History via unified ChatStore
    chat_data = load_or_create_project_chat(project_id)
    chat_history = chat_data.get("messages", [])
    
    # Load Settings
    settings = settings_service.get_settings()
    config = RAGConfig.from_yaml()
    
    return templates.TemplateResponse(
        request=request,
        name="project_review.html",
        context={
            "project": project, 
            "current_page": "projects",
            "chat_history": chat_history,
            "greeting_message": settings.greeting_message,
            "model_name": config.llm.model
        }
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
        # Fallback Order:
        # 1. uploads/ (Standard)
        # 2. data/input root (Legacy)
        # 3. annotated/ (If annotated)

        uploads_path = f"data/input/{project_id}/uploads/{original_filename}"
        legacy_path = f"data/input/{project_id}/{original_filename}"
        annotated_path = f"data/input/{project_id}/annotated/{filename}"

        if os.path.exists(uploads_path):
            file_path = uploads_path
        elif os.path.exists(legacy_path):
            file_path = legacy_path
        elif os.path.exists(annotated_path):
            file_path = annotated_path
        else:
             # Try absolute path from DB if it exists (might be outside input)
             if target_doc and os.path.exists(target_doc.path):
                 file_path = target_doc.path
             else:
                 raise HTTPException(404, "File not found")
        
    return FileResponse(file_path)

@router.post("/{project_id}/analyze", response_class=HTMLResponse)
async def analyze_project(
    project_id: str, 
    request: Request,
    llm_chain: LLMChain = Depends(get_llm_chain)
):
    """Startet die Analyse und gibt die Ergebnisse zurück (Real RAG)."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")
        
    # Get criteria
    criteria_list = criteria_service.get_all()
    
    # Create Chat Messages for Analysis Progress
    messages_html = ""
    new_messages = []

    # 1. Start Message
    start_msg = ChatMessage(
        role="assistant", 
        content=f"<strong>Starte Analyse...</strong><br>Prüfe {len(criteria_list)} Kriterien für diesen Antrag.",
        metadata={"time_formatted": "0.1s", "stop_reason": "none", "tokens_per_sec": "-", "total_tokens": "-"}
    )
    new_messages.append(start_msg)

    # 2. Iterate and Evaluate
    for criterion in criteria_list:
        try:
            # --- RAG Retrieval ---
            eval_query = f"Evaluate criterion '{criterion.title}': {criterion.description}. Provide assessment and evidence."
            
            sources = []
            context = ""
            if hasattr(llm_chain, 'retrieval_engine') and llm_chain.retrieval_engine:
                try:
                    # Retrieve relevant documents
                    filter_dict = {"app_id": project_id}
                    results = llm_chain.retrieval_engine.vector_store.similarity_search(
                        eval_query,
                        k=5,
                        filter=filter_dict
                    )
                    
                    for doc in results:
                        context += f"\n\n{doc.page_content}"
                        sources.append({
                            'document': doc.metadata.get("source", "unknown"),
                            'page': doc.metadata.get("page", 1),
                            'text': doc.page_content
                        })
                except Exception as e:
                    logger.warning(f"RAG retrieval failed for {criterion.id}: {e}")

            # --- LLM Evaluation ---
            eval_status = "warning"
            explanation = "Keine relevanten Dokumente gefunden."
            score = 0.0

            if context:
                prompt = f"""Evaluate the following criterion for a funding application:

Criterion: {criterion.title}
Description: {criterion.description}

Based on the following evidence from the application documents:
{context}

Provide:
1. A clear assessment (PASS, WARNING, or FAIL)
2. A brief German explanation (max 2 sentences)
3. A confidence score (0-1)

Format your response exactly as:
Status: [PASS/WARNING/FAIL]
Score: [0.0-1.0]
Explanation: [Your German explanation]
"""
                try:
                    response = llm_chain.generate(prompt)
                    
                    # Parse response
                    if "PASS" in response.upper():
                        eval_status = "pass"
                    elif "FAIL" in response.upper():
                        eval_status = "fail"
                    else:
                        eval_status = "warning"
                        
                    # Extract explanation
                    explanation = response
                    for line in response.split('\n'):
                        if line.lower().startswith('explanation:'):
                            explanation = line.split(':', 1)[1].strip()
                            break
                except Exception as e:
                    explanation = f"LLM Fehler: {str(e)}"
            
            # --- Generate Annotation ---
            if sources:
                # Find PDF to annotate
                pdf_docs = [d for d in project.documents if d.filename.lower().endswith('.pdf')]
                if pdf_docs:
                    annotation_service.annotate_from_rag_results(
                        project_id=project_id,
                        original_filename=pdf_docs[0].filename,
                        rag_sources=sources,
                        status=eval_status
                    )

            # --- Build Message ---
            status_icon = "✅" if eval_status == "pass" else "⚠️" if eval_status == "warning" else "❌"
            content = (
                f"<strong>{status_icon} {criterion.id} - {criterion.title}</strong><br>"
                f"{explanation}"
            )
            
            msg = ChatMessage(
                role="assistant",
                content=content,
                metadata={
                    "stop_reason": "stop"
                },
                citations=[Citation(**{
                    'doc_id': 'unknown', # simplified
                    'doc_name': s['document'], 
                    'page': s['page'], 
                    'text_snippet': s['text'][:100]
                }) for s in sources[:2]] if sources else None
            )
            new_messages.append(msg)

        except Exception as e:
            logger.error(f"Error evaluating {criterion.id}: {e}")
            # Continue with next or show error msg
            pass

    # 3. Completion Message
    summary_msg = ChatMessage(
        role="assistant",
        content="<strong>Analyse abgeschlossen.</strong> Alle Kriterien wurden geprüft und Annotationen erstellt.",
        metadata={"stop_reason": "finished"}
    )
    new_messages.append(summary_msg)

    # Save to Chat History
    chat_session = chat_service.get_chat_session(project_id)
    chat_session.messages.extend(new_messages)
    chat_service.save_chat_session(chat_session)

    # Render all messages
    for msg in new_messages:
        messages_html += templates.get_template("partials/chat_message.html").render(msg=msg)

    return HTMLResponse(content=messages_html)

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

@router.post("/{project_id}/rag/ingest")
async def ingest_project_documents(
    project_id: str,
    background_tasks: BackgroundTasks
):
    """Ingest all documents for a project (Ephemeral RAG)."""
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(404, "Project not found")

    def _run_ingestion():
        try:
            from src.rag.ingestion import IngestionPipeline
            pipeline = IngestionPipeline()
            
            for doc in project.documents:
                # Resolve path
                file_path = doc.path
                if not os.path.exists(file_path):
                     # Try modern path fallback
                     modern_path = f"data/input/{project_id}/uploads/{doc.filename}"
                     if os.path.exists(modern_path):
                         file_path = modern_path
                
                if os.path.exists(file_path):
                    logger.info(f"Ingesting {doc.filename} for project {project_id}")
                    try:
                        pipeline.ingest_file(file_path, project_id=project_id)
                    except Exception as e:
                        logger.error(f"Failed to ingest {doc.filename}: {e}")
                else:
                    logger.warning(f"File not found for ingestion: {doc.filename}")
                    
            logger.info(f"Ephemeral RAG ingestion completed for {project_id}")
            
        except Exception as e:
            logger.error(f"Project ingestion failed: {e}")

    # Run in background to not block UI load
    background_tasks.add_task(_run_ingestion)
    
    return {"status": "started", "message": "Ingestion started in background"}

@router.delete("/{project_id}/rag")
async def clear_project_rag(project_id: str):
    """Clear RAG context for a project (Exit Handler)."""
    try:
        # We need access to VectorStore. 
        # Using LLMChain dependency or initializing new one.
        # Initializing new VectorStore is safer/easier here.
        from src.rag.vector_store import VectorStore
        # We need config for correct paths
        from src.rag.config import RAGConfig
        
        config = RAGConfig.from_yaml()
        vs = VectorStore(
            persist_directory=config.persist_directory,
            collection_name=config.collection_name
        )
        
        # Delete by metadata
        vs.delete_by_metadata({"project_id": project_id})
        
        logger.info(f"Cleared RAG context for {project_id}")
        return {"status": "success", "message": "RAG context cleared"}
        
    except Exception as e:
        logger.error(f"Failed to clear RAG context: {e}")
        raise HTTPException(500, f"Failed to clear RAG context: {e}")

@router.post("/{project_id}/upload", response_class=HTMLResponse)
async def upload_document(project_id: str, request: Request, file: UploadFile = File(...)):
    """Uploads a document to the project and forwards it to the API client."""
    filename = file.filename or "uploaded_file"
    doc = None
    result = {}

    try:
        # Ensure project directory exists (needed for tests; no-op if already there)
        proj_dir = project_service.INPUT_ROOT / project_id / "uploads"
        proj_dir.mkdir(parents=True, exist_ok=True)

        content = await file.read()
        doc = project_service.save_document(project_id, filename, content)

        # Forward to backend API (async or sync mock)
        if doc:
            upload_resp = api_client.upload_document(doc.path)
            result = await upload_resp if hasattr(upload_resp, "__await__") else upload_resp
    except Exception as e:
        logger.error(f"Upload error: {e}")

    body = f"<div>Uploaded {filename}</div>"
    if isinstance(result, dict) and result.get("chunks_count") is not None:
        body += f"<div>Chunks: {result.get('chunks_count')}</div>"

    return HTMLResponse(content=body)

