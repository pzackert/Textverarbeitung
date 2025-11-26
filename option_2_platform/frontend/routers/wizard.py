from fastapi import APIRouter, Request, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from frontend.mock_data import PROJECTS, CRITERIA
import time

router = APIRouter(prefix="/wizard", tags=["wizard"])
templates = Jinja2Templates(directory="frontend/templates")

def get_project(project_id: str):
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.get("/{project_id}/step/1")
async def step_1(request: Request, project_id: str):
    project = get_project(project_id)
    return templates.TemplateResponse("wizard/step_1.html", {
        "request": request,
        "project": project,
        "step": 1,
        "total_steps": 7
    })

@router.post("/{project_id}/step/1")
async def step_1_submit(request: Request, project_id: str):
    # Logic to save step 1 data
    return RedirectResponse(url=f"/wizard/{project_id}/step/2", status_code=303)

@router.get("/{project_id}/step/2")
async def step_2(request: Request, project_id: str):
    project = get_project(project_id)
    return templates.TemplateResponse("wizard/step_2.html", {
        "request": request,
        "project": project,
        "step": 2,
        "total_steps": 7
    })

@router.post("/{project_id}/step/2/scan")
async def step_2_scan(request: Request, project_id: str):
    # Mock scanning process
    time.sleep(1) # Simulate delay
    return templates.TemplateResponse("wizard/partials/scan_results.html", {
        "request": request,
        "project": get_project(project_id),
        "scanned_docs": [
            {"name": "Handelsregisterauszug", "status": "success", "info": "HRB 12345 gefunden"},
            {"name": "Jahresabschluss", "status": "warning", "info": "Unterschrift fehlt eventuell"},
        ]
    })

@router.post("/{project_id}/step/2")
async def step_2_submit(request: Request, project_id: str):
    return RedirectResponse(url=f"/wizard/{project_id}/step/3", status_code=303)

@router.get("/{project_id}/step/3")
async def step_3(request: Request, project_id: str):
    project = get_project(project_id)
    return templates.TemplateResponse("wizard/step_3.html", {
        "request": request,
        "project": project,
        "criteria": CRITERIA,
        "step": 3,
        "total_steps": 7
    })

@router.post("/{project_id}/step/3")
async def step_3_submit(request: Request, project_id: str):
    return RedirectResponse(url=f"/wizard/{project_id}/step/4", status_code=303)

# ... Implement other steps similarly ...
# For brevity in this turn, I'll implement up to step 3 and a placeholder for the rest.

@router.get("/{project_id}/step/{step_num}")
async def step_generic(request: Request, project_id: str, step_num: int):
    project = get_project(project_id)
    return templates.TemplateResponse(f"wizard/step_{step_num}.html", {
        "request": request,
        "project": project,
        "step": step_num,
        "total_steps": 7
    })

