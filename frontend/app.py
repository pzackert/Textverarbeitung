"""Streamlit entry point for the IFB PROFI wizard (rebuild)."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Dict

import streamlit as st

from frontend.components.command_center import render_command_center
from frontend.components.header import render_header
from frontend.components.sidebar import render_sidebar
from frontend.services import project_service
from frontend.state import session_keys

ASSETS_PATH = Path(__file__).parent / "assets"
STYLES_PATH = Path(__file__).parent / "styles" / "custom.css"


def _mount_styles() -> None:
    if STYLES_PATH.exists():
        st.markdown(STYLES_PATH.read_text(), unsafe_allow_html=True)


def _ensure_demo_seed() -> None:
    session_keys.ensure_defaults()
    if st.session_state.get("seeded_demo"):
        return
    try:
        demo_id = project_service.ensure_demo_project()
        st.session_state["seeded_demo"] = True
        if demo_id and not session_keys.get_active_project():
            session_keys.set_active_project(demo_id)
            session_keys.push_log("Demo-Projekt geladen.")
    except Exception as exc:  # pragma: no cover - defensive
        st.session_state["last_error"] = str(exc)
        session_keys.push_log(f"Demo-Projekt konnte nicht erstellt werden: {exc}")


def _stats(records) -> Dict[str, int | str]:
    return {
        "total": len(records),
        "ready": sum(1 for rec in records if rec.status == "uploaded"),
        "checked": sum(1 for rec in records if rec.status in {"checked", "completed"}),
        "refreshed_at": datetime.now().strftime("%H:%M:%S"),
    }


def main() -> None:
    st.set_page_config(
        page_title="IFB PROFI",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    session_keys.ensure_defaults()
    _mount_styles()
    _ensure_demo_seed()

    projects = project_service.list_projects()
    if projects and not session_keys.get_active_project():
        session_keys.set_active_project(projects[0].id)

    active_id = session_keys.get_active_project()
    active_record = project_service.get_project(active_id)
    latest_results = project_service.load_results(active_id)
    stats = _stats(projects)

    render_header(stats, active_record)
    with st.sidebar:
        render_sidebar(projects)
    render_command_center(projects, active_record, latest_results)


if __name__ == "__main__":
    main()
