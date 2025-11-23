"""Streamlit page to manage the criteria catalog."""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, List

import streamlit as st

st.set_page_config(page_title="Kriterienkatalog", layout="wide")

LOGGER = logging.getLogger("frontend.app")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

PROJECT_ROOT = Path(__file__).resolve().parents[2]
CATALOG_PATH = PROJECT_ROOT / "config" / "kriterienkatalog.json"
DEFAULT_CATALOG = {
    "kriterien": [
        {
            "id": 1,
            "name": "Innovationsgrad",
            "beschreibung": "Technische oder geschäftliche Neuartigkeit des Projekts",
            "kategorie": "Innovation",
            "gewichtung": 9,
        },
        {
            "id": 2,
            "name": "Finanzplan",
            "beschreibung": "Vollständigkeit und Plausibilität der Finanzplanung",
            "kategorie": "Finanzierung",
            "gewichtung": 8,
        },
    ]
}
CATEGORY_OPTIONS = ["Innovation", "Finanzierung", "Team", "Markt"]


def _ensure_catalog_file() -> None:
    if not CATALOG_PATH.exists():
        CATALOG_PATH.parent.mkdir(parents=True, exist_ok=True)
        CATALOG_PATH.write_text(json.dumps(DEFAULT_CATALOG, indent=2), encoding="utf-8")
        LOGGER.info("catalog_created | path=%s", CATALOG_PATH)


def _load_catalog() -> Dict[str, List[Dict[str, Any]]]:
    _ensure_catalog_file()
    try:
        with CATALOG_PATH.open("r", encoding="utf-8") as file:
            data = json.load(file)
            if "kriterien" not in data or not isinstance(data["kriterien"], list):
                LOGGER.warning("catalog_structure_invalid | path=%s", CATALOG_PATH)
                return DEFAULT_CATALOG.copy()
            return data
    except json.JSONDecodeError as exc:
        LOGGER.error("catalog_json_error | %s", exc)
        st.error("Kriterienkatalog konnte nicht geladen werden. Bitte JSON prüfen.")
        return DEFAULT_CATALOG.copy()


def _save_catalog(data: Dict[str, List[Dict[str, Any]]]) -> None:
    with CATALOG_PATH.open("w", encoding="utf-8") as file:
        json.dump(data, file, indent=2, ensure_ascii=False)
    LOGGER.info("catalog_saved | count=%s", len(data.get("kriterien", [])))


def _next_id(criteria: List[Dict[str, Any]]) -> int:
    return max((entry.get("id", 0) for entry in criteria), default=0) + 1


def _log_event(event: str, **details: Any) -> None:
    if details:
        LOGGER.info("%s | %s", event, details)
    else:
        LOGGER.info("%s", event)


LOGGER.info("page_view | {'page': 'kriterienkatalog'}")

st.title("📋 Kriterienkatalog")
st.caption("Diese Kriterien werden für die Bewertung von Förderanträgen geprüft")

catalog = _load_catalog()
criteria = catalog.get("kriterien", [])

st.subheader("Kriterien-Übersicht")
if criteria:
    st.dataframe(criteria, use_container_width=True)
else:
    st.info("Noch keine Kriterien vorhanden.")

st.divider()

st.subheader("➕ Neues Kriterium hinzufügen")
name = st.text_input("Kriterienname", key="new_criterion_name")
description = st.text_area("Beschreibung", key="new_criterion_description")
category = st.selectbox("Kategorie", options=CATEGORY_OPTIONS, key="new_criterion_category")
weight = st.number_input(
    "Gewichtung",
    min_value=1,
    max_value=10,
    value=5,
    step=1,
    key="new_criterion_weight",
)

if st.button("Kriterium speichern", use_container_width=True):
    if not name.strip() or not description.strip():
        st.warning("Bitte gib mindestens einen Namen und eine Beschreibung an.")
    else:
        new_entry = {
            "id": _next_id(criteria),
            "name": name.strip(),
            "beschreibung": description.strip(),
            "kategorie": category,
            "gewichtung": int(weight),
        }
        criteria.append(new_entry)
        catalog["kriterien"] = criteria
        _save_catalog(catalog)
        _log_event("criterion_added", criterion_id=new_entry["id"], name=new_entry["name"])
        st.success("Kriterium gespeichert.")
        st.experimental_rerun()
