from typing import List, Optional
from datetime import datetime
from time import perf_counter
from fastapi import APIRouter, HTTPException, status, BackgroundTasks
from src.api.schemas_criteria import Criterion, CreateCriterionRequest, UpdateCriterionRequest
from src.services.criteria_service import criteria_service
from src.services.validation_service import validation_service
from src.services.criteria_results_store import (
    load_criteria_results,
    get_evaluation_summary,
)
from src.services.criteria_results_store import save_criterion_result  # for typing only
from src.services.project_service import project_service

router = APIRouter(prefix="/criteria", tags=["criteria"])
eval_router = APIRouter(prefix="/projects", tags=["criteria_evaluation"])

@router.get("", response_model=List[Criterion])
async def list_criteria():
    return criteria_service.get_all()

@router.get("/{criterion_id}", response_model=Criterion)
async def get_criterion(criterion_id: str):
    criterion = criteria_service.get_by_id(criterion_id)
    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    return criterion

@router.post("", response_model=Criterion, status_code=status.HTTP_201_CREATED)
async def create_criterion(request: CreateCriterionRequest):
    try:
        return criteria_service.create(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{criterion_id}", response_model=Criterion)
async def update_criterion(criterion_id: str, request: UpdateCriterionRequest):
    criterion = criteria_service.update(criterion_id, request)
    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    return criterion

@router.delete("/{criterion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_criterion(criterion_id: str):
    success = criteria_service.delete(criterion_id)
    if not success:
        raise HTTPException(status_code=404, detail="Criterion not found")
    return None


@eval_router.post("/{project_id}/criteria/{criterion_id}/evaluate")
async def evaluate_criterion(project_id: str, criterion_id: str):
    """Trigger evaluation of a single criterion for a project."""
    try:
        return validation_service.evaluate_criterion(project_id, criterion_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Failed to evaluate criterion: {exc}")


@eval_router.get("/{project_id}/criteria/{criterion_id}/annotations")
async def list_annotations_for_criterion(project_id: str, criterion_id: str):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not project.validation_results or criterion_id not in project.validation_results:
        return {
            "criterion_id": criterion_id,
            "criterion_name": None,
            "annotations": [],
        }

    result = project.validation_results.get(criterion_id, {})
    annotations = result.get("annotations", [])
    return {
        "criterion_id": criterion_id,
        "criterion_name": result.get("criterion_name"),
        "annotations": annotations,
    }


# --- Criteria results persistence endpoints ---

@eval_router.get("/{project_id}/criteria/results")
async def get_all_criteria_results(project_id: str):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return load_criteria_results(project_id)


@eval_router.get("/{project_id}/criteria/results/summary")
async def get_criteria_results_summary(project_id: str):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return get_evaluation_summary(project_id)


@eval_router.get("/{project_id}/criteria/{criterion_id}/result")
async def get_single_criterion_result(project_id: str, criterion_id: str):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    data = load_criteria_results(project_id)
    crit = data.get("criteria_results", {}).get(criterion_id)
    if not crit:
        raise HTTPException(status_code=404, detail="Criterion result not found")
    return crit


# --- Bulk evaluation ---

evaluation_jobs = {}


def _bulk_job_key(project_id: str, job_id: str) -> str:
    return f"{project_id}:{job_id}"


def _run_bulk_evaluation(project_id: str, job_id: str, criteria_ids: list[str]):
    key = _bulk_job_key(project_id, job_id)
    evaluation_jobs[key] = {
        "job_id": job_id,
        "status": "running",
        "progress": {
            "total": len(criteria_ids),
            "completed": 0,
            "current_criterion": None,
            "current_status": None,
            "results": [],
        },
        "started_at": datetime.utcnow().isoformat() + "Z",
    }

    start_all = perf_counter()
    for idx, crit_id in enumerate(criteria_ids):
        evaluation_jobs[key]["progress"]["current_criterion"] = crit_id
        evaluation_jobs[key]["progress"]["current_status"] = "running"
        single_start = perf_counter()
        try:
            res = validation_service.evaluate_criterion(project_id, crit_id)
            duration = round(perf_counter() - single_start, 3)
            evaluation_jobs[key]["progress"]["results"].append(
                {
                    "criterion_id": crit_id,
                    "status": res.get("status"),
                    "completed": True,
                    "duration_sec": duration,
                }
            )
        except Exception as exc:
            evaluation_jobs[key]["progress"]["results"].append(
                {
                    "criterion_id": crit_id,
                    "status": "error",
                    "completed": True,
                    "error": str(exc),
                }
            )
        evaluation_jobs[key]["progress"]["completed"] = idx + 1

    total_duration = round(perf_counter() - start_all, 3)
    evaluation_jobs[key]["status"] = "completed"
    evaluation_jobs[key]["completed_at"] = datetime.utcnow().isoformat() + "Z"
    evaluation_jobs[key]["total_duration_sec"] = total_duration

    # summary counts
    summary_counts = {}
    for item in evaluation_jobs[key]["progress"]["results"]:
        status = item.get("status")
        if status:
            summary_counts[status] = summary_counts.get(status, 0) + 1
    evaluation_jobs[key]["progress"]["summary"] = summary_counts


@eval_router.post("/{project_id}/criteria/evaluate-all")
async def evaluate_all_criteria(
    project_id: str,
    background_tasks: BackgroundTasks,
    criteria_ids: Optional[List[str]] = None,
):
    project = project_service.get_project(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    all_ids = [c.id for c in criteria_service.get_all()]
    selected = criteria_ids or all_ids
    job_id = f"eval_all_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{len(selected)}"

    background_tasks.add_task(_run_bulk_evaluation, project_id, job_id, selected)

    return {
        "project_id": project_id,
        "job_id": job_id,
        "status": "started",
        "total_criteria": len(selected),
        "criteria_ids": selected,
    }


@eval_router.get("/{project_id}/criteria/evaluate-all/{job_id}/status")
async def get_bulk_status(project_id: str, job_id: str):
    key = _bulk_job_key(project_id, job_id)
    job = evaluation_jobs.get(key)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    # compute estimated remaining
    prog = job.get("progress", {})
    done = prog.get("completed", 0)
    total = prog.get("total", 0)
    durations = [r.get("duration_sec") for r in prog.get("results", []) if r.get("duration_sec")]
    avg = sum(durations) / len(durations) if durations else 0
    remaining = max(total - done, 0) * avg
    job["estimated_remaining_sec"] = round(remaining, 2)
    return job
