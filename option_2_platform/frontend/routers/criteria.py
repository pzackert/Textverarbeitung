from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from src.services.criteria_service import criteria_service
from src.api.schemas_criteria import CreateCriterionRequest, UpdateCriterionRequest

router = APIRouter(prefix="/criteria", tags=["criteria"])

# Define templates path relative to where main.py runs
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("", response_class=HTMLResponse)
async def list_criteria(request: Request):
    """
    Shows the list of all criteria.
    """
    criteria = criteria_service.get_all()
    # Sort criteria by ID
    criteria.sort(key=lambda x: x.id)
    return templates.TemplateResponse(
        request=request,
        name="criteria_list.html",
        context={"criteria": criteria}
    )

@router.get("/new", response_class=HTMLResponse)
async def new_criterion_form(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="criteria_edit.html",
        context={"criterion": None, "mode": "create"}
    )

@router.post("/new", response_class=HTMLResponse)
async def create_criterion(
    request: Request,
    id: str = Form(...),
    name: str = Form(...),
    kategorie: str = Form(...),
    kurz: str = Form(...),
    lang: str = Form(...),
    prompt: str = Form(""),
    recommended: bool = Form(False)
):
    try:
        req = CreateCriterionRequest(
            id=id, name=name, kategorie=kategorie, kurz=kurz, lang=lang, prompt=prompt, recommended=recommended
        )
        criteria_service.create(req)
        return RedirectResponse(url="/criteria", status_code=303)
    except ValueError as e:
        return templates.TemplateResponse(
            request=request,
            name="criteria_edit.html",
            context={"criterion": req.dict(), "mode": "create", "error": str(e)}
        )

@router.get("/{id}/edit", response_class=HTMLResponse)
async def edit_criterion_form(request: Request, id: str):
    criterion = criteria_service.get_by_id(id)
    if not criterion:
        return RedirectResponse(url="/criteria")
    return templates.TemplateResponse(
        request=request,
        name="criteria_edit.html",
        context={"criterion": criterion, "mode": "edit"}
    )

@router.post("/{id}/edit", response_class=HTMLResponse)
async def update_criterion(
    request: Request,
    id: str,
    name: str = Form(...),
    kategorie: str = Form(...),
    kurz: str = Form(...),
    lang: str = Form(...),
    prompt: str = Form(""),
    recommended: bool = Form(False)
):
    req = UpdateCriterionRequest(
        name=name, kategorie=kategorie, kurz=kurz, lang=lang, prompt=prompt, recommended=recommended
    )
    criteria_service.update(id, req)
    return RedirectResponse(url="/criteria", status_code=303)

@router.post("/{id}/delete", response_class=HTMLResponse)
async def delete_criterion_route(request: Request, id: str):
    criteria_service.delete(id)
    return RedirectResponse(url="/criteria", status_code=303)
