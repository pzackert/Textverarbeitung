"""Streamlit page to manage funding applications overview."""
from __future__ import annotations

import logging
from typing import Any

import streamlit as st

LOGGER = logging.getLogger("frontend.app")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)


def _log_event(event: str, **details: Any) -> None:
    if details:
        LOGGER.info("%s | %s", event, details)
    else:
        LOGGER.info("%s", event)


LOGGER.info("page_view | {'page': 'antragsuebersicht'}")

st.set_page_config(page_title="Antragsübersicht", layout="wide")
st.title("📊 Antragsübersicht")

st.subheader("➕ Neues Projekt anlegen")
if st.button("Neuen Antrag starten", use_container_width=True):
    _log_event("navigate_new_project")
    st.switch_page("pages/02_Projekt.py")

st.divider()

st.subheader("📋 Übersicht aller Projektanträge")
projects = [
    {
        "Projekt-ID": "PRJ-2025-001",
        "Antragsteller": "UrbanGrow GmbH",
        "Eingangsdatum": "03.11.2025",
        "Status": "In Prüfung",
        "Letzte Bearbeitung": "15.11.2025",
        "Aktion": "Öffnen",
    },
    {
        "Projekt-ID": "PRJ-2025-002",
        "Antragsteller": "HanseTech AG",
        "Eingangsdatum": "29.10.2025",
        "Status": "Neu",
        "Letzte Bearbeitung": "29.10.2025",
        "Aktion": "Öffnen",
    },
    {
        "Projekt-ID": "PRJ-2025-003",
        "Antragsteller": "CleanWave Startups",
        "Eingangsdatum": "20.10.2025",
        "Status": "Abgeschlossen",
        "Letzte Bearbeitung": "05.11.2025",
        "Aktion": "Öffnen",
    },
    {
        "Projekt-ID": "PRJ-2025-004",
        "Antragsteller": "Nordwind Solutions",
        "Eingangsdatum": "12.11.2025",
        "Status": "In Prüfung",
        "Letzte Bearbeitung": "16.11.2025",
        "Aktion": "Öffnen",
    },
]

st.table(projects)

st.caption("Aktion-Buttons öffnen die Detailseite des jeweiligen Projekts.")

for project in projects:
    cols = st.columns([5, 1])
    with cols[0]:
        st.write(
            f"**{project['Projekt-ID']}** – {project['Antragsteller']} | Status: {project['Status']}"
        )
    with cols[1]:
        if st.button("Öffnen", key=f"open_{project['Projekt-ID']}"):
            _log_event("open_project", project_id=project["Projekt-ID"])
            st.session_state["current_project_id"] = project["Projekt-ID"]
            st.switch_page("pages/02_Projekt.py")
