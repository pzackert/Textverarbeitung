import json
from pathlib import Path

import pytest

from src.services import project_service as ps_module
from src.services import criteria_results_store as crs_module


def _configure_tmp(monkeypatch, tmp_path: Path):
    # Redirect service roots to temp path
    monkeypatch.setattr(ps_module, "INPUT_ROOT", tmp_path)
    monkeypatch.setattr(crs_module, "BASE_DIR", tmp_path)


def test_heal_creates_missing_files(monkeypatch, tmp_path):
    _configure_tmp(monkeypatch, tmp_path)

    project_id = "p1"
    project_dir = tmp_path / project_id
    project_dir.mkdir(parents=True)
    # leave only uploads folder missing to ensure creation; no metadata/chat/criteria present

    reports = ps_module.project_service.heal_all_projects()

    assert {r["project_id"] for r in reports} == {project_id}

    # metadata.json exists and is valid
    meta_path = project_dir / "metadata.json"
    assert meta_path.exists()
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta["id"] == project_id
    assert meta["status"] == "Entwurf"

    # chat_history.json exists with messages array
    chat_path = project_dir / "chat_history.json"
    chat = json.loads(chat_path.read_text(encoding="utf-8"))
    assert chat.get("messages") == []

    # criteria_responses.json exists and has summary totals
    crit_path = project_dir / "criteria_responses.json"
    data = json.loads(crit_path.read_text(encoding="utf-8"))
    assert data["project_id"] == project_id
    assert "summary" in data
    assert data["summary"]["total"] == len(crs_module.criteria_service.get_all())

    # folders uploads/annotated exist
    assert (project_dir / "uploads").exists()
    assert (project_dir / "annotated").exists()


def test_heal_recovers_corrupt_metadata(monkeypatch, tmp_path):
    _configure_tmp(monkeypatch, tmp_path)

    project_id = "p2"
    project_dir = tmp_path / project_id
    project_dir.mkdir(parents=True)
    # corrupt metadata
    (project_dir / "metadata.json").write_text("{corrupt", encoding="utf-8")
    # corrupt chat
    (project_dir / "chat_history.json").write_text("not-json", encoding="utf-8")
    # corrupt criteria
    (project_dir / "criteria_responses.json").write_text("[]", encoding="utf-8")

    ps_module.project_service.heal_all_projects()

    # metadata healed
    meta = json.loads((project_dir / "metadata.json").read_text(encoding="utf-8"))
    assert meta["id"] == project_id
    # chat healed
    chat = json.loads((project_dir / "chat_history.json").read_text(encoding="utf-8"))
    assert chat.get("messages") == []
    # criteria healed to dict with summary
    crit = json.loads((project_dir / "criteria_responses.json").read_text(encoding="utf-8"))
    assert isinstance(crit.get("criteria_results"), dict)
    assert crit["summary"]["total"] == len(crs_module.criteria_service.get_all())
