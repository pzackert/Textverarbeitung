"""Sidebar (project selector) implementation."""
from __future__ import annotations

from typing import List

import streamlit as st

from frontend.components.toast import show_toast
from frontend.services import project_service
from frontend.state import session_keys


def _format_option(record: project_service.ProjectRecord) -> str:
    return f"{record.name} ({record.status_label})"


def _trigger_rerun() -> None:
    try:
        st.rerun()
    except AttributeError:  # pragma: no cover
        st.experimental_rerun()


def render_sidebar(records: List[project_service.ProjectRecord]) -> None:
    """Render project filter, selector, and creation form."""

    session_keys.ensure_defaults()
    st.subheader("Projekte")
    filter_text = st.text_input("Filter", key="project_filter", placeholder="Name oder Status")
    filtered = [
        rec
        for rec in records
        if not filter_text or filter_text.lower() in rec.name.lower() or filter_text.lower() in rec.status.lower()
    ]
    if not filtered:
        st.info("Keine Projekte gefunden.")
    else:
        options = [rec.id for rec in filtered]
        lookup = {rec.id: rec for rec in filtered}
        active_id = session_keys.get_active_project()
        index = options.index(active_id) if active_id in options else 0
        selected_id = st.radio(
            "Aktives Projekt",
            options=options,
            index=index,
            format_func=lambda project_id: _format_option(lookup[project_id]),
        )
        if selected_id != active_id:
            session_keys.set_active_project(selected_id)
            session_keys.push_log(f"Projekt gewechselt zu {lookup[selected_id].name}")
            _trigger_rerun()

    col_a, col_b = st.columns(2)
    if col_a.button("Aktualisieren", use_container_width=True):
        session_keys.push_log("Projektliste aktualisiert")
        _trigger_rerun()
    if col_b.button("Demo laden", use_container_width=True):
        demo_id = project_service.ensure_demo_project()
        if demo_id:
            session_keys.set_active_project(demo_id)
            show_toast("Demo-Projekt bereit.", tone="success")
            _trigger_rerun()
        else:
            show_toast("Demo konnte nicht erstellt werden.", tone="error")

    with st.expander("Neues Projekt anlegen"):
        with st.form("create-project-form"):
            projekt_name = st.text_input("Projektname *")
            antragsteller = st.text_input("Antragsteller")
            modul = st.selectbox("Modul", ["PROFI Standard", "PROFI Light", "PROFI Express"])
            projektart = st.selectbox("Projektart", ["Forschung", "Entwicklung", "Pilot"])
            beschreibung = st.text_area("Kurzbeschreibung")
            submitted = st.form_submit_button("Projekt erstellen", use_container_width=True)
            if submitted:
                projekt_id, error = project_service.create_project(
                    {
                        "projekt_name": projekt_name.strip(),
                        "antragsteller": antragsteller.strip(),
                        "modul": modul,
                        "projektart": projektart,
                        "beschreibung": beschreibung.strip() or None,
                    }
                )
                if error:
                    st.error(error)
                else:
                    show_toast("Projekt angelegt.", tone="success")
                    session_keys.push_log(f"Neues Projekt erstellt: {projekt_name}")
                    session_keys.set_active_project(projekt_id)
                    _trigger_rerun()
