"""Command Center composition for the IFB PROFI Streamlit UI."""
from __future__ import annotations

from datetime import date, timedelta
from typing import Iterable, List, Optional, Sequence

import streamlit as st

from frontend.components import results_view, review_dashboard, upload_panel
from frontend.components.toast import show_toast
from frontend.services import analytics_service, process_service, project_service
from frontend.state import session_keys


def _cached_heatmap(start_iso: str, end_iso: str, count: int):
    start = date.fromisoformat(start_iso)
    end = date.fromisoformat(end_iso)
    return analytics_service.get_daily_stats(start, end, count)


def _render_quick_actions(active_record: Optional[project_service.ProjectRecord]) -> None:
    col_a, col_b, col_c = st.columns(3)
    col_a.button("Neues Projekt", help="Formular in der Sidebar nutzen.", disabled=True)
    ready = bool(active_record and project_service.required_documents_status(active_record))
    col_b.button("Uploads pruefen", help="Siehe Upload Tab", disabled=not active_record)
    col_c.button("Live-Check starten", disabled=not ready)


def _render_live_check(record: Optional[project_service.ProjectRecord]) -> None:
    session_keys.ensure_defaults()
    if not record:
        st.info("Bitte zuerst ein Projekt waehlen.")
        return

    required_status = project_service.required_documents_status(record)
    ready = bool(required_status and all(required_status.values()))
    st.metric("Process Step", f"{record.current_step}/4")
    st.progress(min(record.current_step / 4, 1.0))
    if required_status:
        st.write({"Pflicht": required_status})

    disabled = not ready or st.session_state.get("processing", False)
    if st.button("Kriterienlauf starten", disabled=disabled, use_container_width=True):
        session_keys.set_processing(True)
        session_keys.push_log("Starte Kriterienlauf...")
        with st.spinner("LLM prueft Kriterien..."):
            result = process_service.run_criteria_check(record.id)
        session_keys.set_processing(False)
        if result.get("ok"):
            session_keys.push_log("Kriterienlauf abgeschlossen.")
            if result.get("results"):
                session_keys.store_results(result["results"])
            show_toast("Prueflauf abgeschlossen.", tone="success")
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
        else:
            message = result.get("message", "Fehler im Kriterienlauf")
            st.error(message)
            session_keys.push_log(f"Pruefung fehlgeschlagen: {message}")

    st.markdown("#### Terminal")
    logs = st.session_state.get("terminal_logs", [])[-15:]
    st.code("\n".join(logs) or "Noch keine Logs.")
    st.text_area(
        "KI-Chat (Stub)",
        value="",
        placeholder="Feature folgt in Phase 2...",
        disabled=True,
    )


def render_command_center(
    records: Sequence[project_service.ProjectRecord],
    active_record: Optional[project_service.ProjectRecord],
    latest_results: Optional[dict],
) -> None:
    """Render overview, upload workflow, live-check, and results tabs."""

    session_keys.ensure_defaults()
    _render_quick_actions(active_record)

    days = int(st.session_state.get("heatmap_days", 120))
    today = date.today()
    start = today - timedelta(days=days)
    heatmap_data = _cached_heatmap(start.isoformat(), today.isoformat(), len(records) or 1)

    overview_tab, upload_tab, live_tab, results_tab = st.tabs(
        ["Uebersicht", "Uploads", "Live-Pruefung", "Ergebnisse"]
    )

    with overview_tab:
        review_dashboard.render_review_dashboard(records, active_record, heatmap_data)

    with upload_tab:
        upload_panel.render_upload_panel(active_record)

    with live_tab:
        _render_live_check(active_record)

    with results_tab:
        fallback_results = latest_results or st.session_state.get("last_results")
        results_view.render_results_view(active_record, fallback_results)
