from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

# Define templates path relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

from src.services.system_state import system_state

@router.get("/")
async def dashboard(request: Request):
    """
    Renders dashboard or startup screen based on state.
    """
    if system_state.status != "ready":
         return templates.TemplateResponse(
            request=request,
            name="startup.html",
            context={}
        )

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"current_page": "dashboard"} 
    )
