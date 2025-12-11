from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from pathlib import Path

router = APIRouter(prefix="/logo", tags=["logo"])
# Fix template path
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("", response_class=HTMLResponse)
async def logo_showcase(request: Request):
    """Showcase for IFB Logo Animations."""
    return templates.TemplateResponse(
        request=request,
        name="logo.html",
        context={"current_page": "logo"}
    )
