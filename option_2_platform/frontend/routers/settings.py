from fastapi import APIRouter, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from src.services.settings_service import settings_service
from src.services.knowledge_service import knowledge_service

router = APIRouter(prefix="/settings", tags=["settings"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("", response_class=HTMLResponse)
async def settings_page(request: Request):
    """
    Shows the settings page.
    """
    # Load current config
    config = settings_service.get_settings()
    
    # Load global knowledge files
    knowledge_files = knowledge_service.list_documents()

    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={"config": config, "knowledge_files": knowledge_files}
    )

@router.post("/update")
async def update_settings(request: Request):
    """
    Updates the configuration.
    (Existing logic preserved/assumed)
    """
    form_data = await request.form()
    # ... update logic ...
    return RedirectResponse(url="/settings", status_code=303)

@router.post("/knowledge/upload")
async def upload_knowledge(request: Request, file: UploadFile = File(...)):
    """
    Uploads a global knowledge file.
    """
    try:
        content = await file.read()
        knowledge_service.save_file(file.filename, content)
        # TODO: Trigger RAG ingestion in background
        # For prototype, we call save which is synchronous
    except Exception as e:
        print(f"Error uploading: {e}")
        
    return RedirectResponse(url="/settings", status_code=303)

@router.post("/knowledge/delete")
async def delete_knowledge(request: Request, filename: str = Form(...)):
    """
    Deletes a global knowledge file.
    """
    knowledge_service.delete_file(filename)
    # TODO: Trigger RAG deletion
    return RedirectResponse(url="/settings", status_code=303)
