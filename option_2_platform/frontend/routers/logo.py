from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/logo", tags=["logo"])
templates = Jinja2Templates(directory="frontend/templates")

@router.get("", response_class=HTMLResponse)
async def logo_showcase(request: Request):
    """Showcase for IFB Logo Animations."""
    return templates.TemplateResponse(
        request=request,
        name="logo.html",
        context={"current_page": "logo"}
    )
