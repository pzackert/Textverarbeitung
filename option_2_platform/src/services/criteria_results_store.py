import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from src.services.criteria_service import criteria_service
from src.services.project_service import project_service

BASE_DIR = Path("data/input")


def _base_structure(project_id: str) -> Dict[str, Any]:
    project = project_service.get_project(project_id)
    total_criteria = len(criteria_service.get_all())
    return {
        "project_id": project_id,
        "project_name": project.name if project else None,
        "company": getattr(project, "applicant", None) if project else None,
        "last_evaluation": None,
        "total_criteria": total_criteria,
        "criteria_results": {},
        "summary": {
            "total": total_criteria,
            "evaluated": 0,
            "pending": total_criteria,
            "status_counts": {},
        },
    }


def _results_path(project_id: str) -> Path:
    return BASE_DIR / project_id / "criteria_responses.json"


def _recompute_summary(data: Dict[str, Any]) -> None:
    total = len(criteria_service.get_all())
    evaluated = len(data.get("criteria_results", {}))
    status_counts: Dict[str, int] = {}
    for item in data.get("criteria_results", {}).values():
        status = item.get("status")
        if status:
            status_counts[status] = status_counts.get(status, 0) + 1
    data["total_criteria"] = total
    data.setdefault("summary", {})
    data["summary"].update(
        {
            "total": total,
            "evaluated": evaluated,
            "pending": max(total - evaluated, 0),
            "status_counts": status_counts,
        }
    )


def load_criteria_results(project_id: str) -> Dict[str, Any]:
    path = _results_path(project_id)
    if not path.exists():
        data = _base_structure(project_id)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, ensure_ascii=False, indent=2)
        return data

    with open(path, "r", encoding="utf-8") as handle:
        data = json.load(handle)

    _recompute_summary(data)
    return data


def save_criterion_result(project_id: str, criterion_result: Dict[str, Any]) -> Dict[str, Any]:
    data = load_criteria_results(project_id)
    crit_id = criterion_result.get("criterion_id")
    if not crit_id:
        return data

    data.setdefault("criteria_results", {})
    data["criteria_results"][crit_id] = criterion_result
    data["last_evaluation"] = datetime.utcnow().isoformat() + "Z"

    _recompute_summary(data)

    path = _results_path(project_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as handle:
        json.dump(data, handle, ensure_ascii=False, indent=2)

    return data


def get_evaluation_summary(project_id: str) -> Dict[str, Any]:
    data = load_criteria_results(project_id)
    return data.get("summary", {})
