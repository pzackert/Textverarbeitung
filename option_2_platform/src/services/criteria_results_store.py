import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from src.services.criteria_service import criteria_service
from src.services.project_service import project_service

BASE_DIR = Path("data/input")


def _atomic_write(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
    tmp_path.replace(path)


def _metadata_path(project_id: str) -> Path:
    return BASE_DIR / project_id / "metadata.json"


def _mirror_summary_to_metadata(project_id: str, data: Dict[str, Any]) -> None:
    """Persist criteria summary/last_evaluation into metadata.json for quick access."""
    meta_path = _metadata_path(project_id)
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8")) if meta_path.exists() else {}
        if not isinstance(meta, dict):
            raise ValueError("metadata invalid")
    except Exception:
        meta = {"id": project_id, "name": project_id, "status": "Entwurf"}

    meta["last_evaluation"] = data.get("last_evaluation")
    meta["criteria_summary"] = data.get("summary", {})
    meta.setdefault("created_at", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
    meta["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    _atomic_write(meta_path, meta)


def _base_structure(project_id: str) -> Dict[str, Any]:
    total_criteria = len(criteria_service.get_all())
    return {
        "project_id": project_id,
        "project_name": project_id,
        "company": None,
        "last_evaluation": None,
        "total_criteria": total_criteria,
        "criteria_results": {},
        "pruefungen": [],
        "summary": {
            "total": total_criteria,
            "evaluated": 0,
            "pending": total_criteria,
            "status_counts": {},
        },
    }


def _results_path(project_id: str) -> Path:
    return BASE_DIR / project_id / "criteria_responses.json"


def has_criteria_results(project_id: str) -> bool:
    """Return True if criteria_responses.json exists and has at least one result."""
    path = _results_path(project_id)
    if not path.exists():
        return False

    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        crit = raw.get("criteria_results") if isinstance(raw, dict) else None
        return bool(crit)
    except Exception:
        return False


def _recompute_summary(data: Dict[str, Any]) -> None:
    total = len(criteria_service.get_all())
    evaluated = len(data.get("criteria_results", {}))
    status_counts: Dict[str, int] = {}
    for item in data.get("criteria_results", {}).values():
        status = item.get("status")
        if status:
            status_counts[status] = status_counts.get(status, 0) + 1
    data.setdefault("pruefungen", [])
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
    data: Dict[str, Any]
    try:
        if not path.exists():
            raise FileNotFoundError("criteria_responses.json missing")

        with open(path, "r", encoding="utf-8") as handle:
            data = json.load(handle)
            if not isinstance(data, dict):
                raise ValueError("criteria_responses.json invalid shape")
    except Exception:
        # Heal file on missing/corrupt content
        data = _base_structure(project_id)
        _atomic_write(path, data)

    _recompute_summary(data)
    _mirror_summary_to_metadata(project_id, data)
    return data


def save_criterion_result(project_id: str, criterion_result: Dict[str, Any]) -> Dict[str, Any]:
    data = load_criteria_results(project_id)
    crit_id = criterion_result.get("criterion_id")
    if not crit_id:
        return data

    data.setdefault("criteria_results", {})
    data["criteria_results"][crit_id] = criterion_result
    data["last_evaluation"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # Maintain array-based view for UI and docs
    data.setdefault("pruefungen", [])
    data["pruefungen"] = [p for p in data["pruefungen"] if p.get("criterion_id") != crit_id]
    data["pruefungen"].append(
        {
            "criterion_id": criterion_result.get("criterion_id"),
            "kriterium_id": criterion_result.get("criterion_id"),
            "kriterium_name": criterion_result.get("criterion_name"),
            "status": criterion_result.get("status"),
            "begruendung": criterion_result.get("begruendung") or criterion_result.get("reason"),
            "dokument": criterion_result.get("dokument"),
            "referenz": criterion_result.get("referenz"),
            "geprueft_am": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            "evidence": criterion_result.get("evidence", []),
        }
    )

    _recompute_summary(data)

    path = _results_path(project_id)
    _atomic_write(path, data)
    _mirror_summary_to_metadata(project_id, data)

    return data


def get_evaluation_summary(project_id: str) -> Dict[str, Any]:
    data = load_criteria_results(project_id)
    return data.get("summary", {})
