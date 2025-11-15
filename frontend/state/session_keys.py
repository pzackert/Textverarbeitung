"""Central definition of Streamlit session state keys and defaults."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

import streamlit as st

SESSION_DEFAULTS: Dict[str, Any] = {
    "ui_mode": "dashboard",
    "active_project": None,
    "terminal_logs": [],
    "criteria_state": [],
    "messages": [],
    "processing": False,
    "project_filter": "",
    "last_results": None,
    "seeded_demo": False,
    "last_error": None,
    "heatmap_days": 120,
}


def ensure_defaults() -> None:
    """Ensure that every known key exists in `st.session_state`."""
    for key, value in SESSION_DEFAULTS.items():
        if key not in st.session_state:
            st.session_state[key] = value if not isinstance(value, list) else list(value)


def set_active_project(project_id: str | None) -> None:
    ensure_defaults()
    st.session_state["active_project"] = project_id


def get_active_project() -> str | None:
    ensure_defaults()
    return st.session_state.get("active_project")


def set_processing(state: bool) -> None:
    ensure_defaults()
    st.session_state["processing"] = state


def push_log(message: str) -> None:
    ensure_defaults()
    timestamp = datetime.now().strftime("%H:%M:%S")
    entry = f"[{timestamp}] {message}"
    logs: List[str] = st.session_state["terminal_logs"]
    logs.append(entry)
    st.session_state["terminal_logs"] = logs[-200:]


def store_results(results: Dict[str, Any]) -> None:
    ensure_defaults()
    st.session_state["last_results"] = results
