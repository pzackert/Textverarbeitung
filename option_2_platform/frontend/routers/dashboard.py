from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()

# Define templates path relative to this file
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("/")
async def dashboard(request: Request):
    """
    Renders the empty dashboard shell.
    Data is fetched client-side via /api/system/status polling.
    """
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"current_page": "dashboard"} 
    )
