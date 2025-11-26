from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from frontend.mock_data import CRITERIA

router = APIRouter()
templates = Jinja2Templates(directory="frontend/templates")

@router.get("/kriterien")
async def list_criteria(request: Request):
    return templates.TemplateResponse("criteria_list.html", {
        "request": request,
        "criteria": CRITERIA
    })
