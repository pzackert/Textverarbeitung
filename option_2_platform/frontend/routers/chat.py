from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(prefix="/chat", tags=["frontend_chat"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("", response_class=HTMLResponse)
async def chat_page(request: Request):
    """
    Renders the Global Chat interface.
    """
    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={} 
    )
