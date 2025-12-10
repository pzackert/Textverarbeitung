from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from src.services.settings_service import settings_service

router = APIRouter(prefix="/settings", tags=["settings"])
templates = Jinja2Templates(directory="frontend/templates")

@router.get("", response_class=HTMLResponse)
async def settings_page(request: Request):
    settings = settings_service.get_settings()
    
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
        context={
            "settings": settings,
            "current_page": "settings"
        }
    )

@router.post("", response_class=HTMLResponse)
async def update_settings(
    request: Request,
    greeting_message: str = Form(...),
    system_prompt: str = Form(...)
):
    settings_service.update_settings(greeting_message, system_prompt)
    
    # Reload with success message? Or Redirect?
    # Redirect is standard.
    return RedirectResponse(url="/settings", status_code=303)
