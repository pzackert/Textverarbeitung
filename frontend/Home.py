"""Streamlit multipage entry-point for the IFB PROFI prototype."""
from __future__ import annotations

import logging

import streamlit as st

LOGGER = logging.getLogger("frontend.app")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)

HOME_TITLE = "🤖 IFB PROFI - KI-gestützte Dokumentenverarbeitung"
HOME_SUBTITLE = "Willkommen zur automatisierten Dokumentenprüfung für das IFB PROFI-Programm."


def _log_event(event: str, **details: str | int | float | None) -> None:
    """Helper to log structured interaction events."""
    if details:
        LOGGER.info("%s | %s", event, details)
    else:
        LOGGER.info("%s", event)


def main() -> None:
    """Render the HOME page."""
    st.set_page_config(page_title="Home", layout="centered")
    _log_event("page_view", page="home")

    st.title(HOME_TITLE)
    st.write(HOME_SUBTITLE)

    st.header("Willkommen bei der KI-gestützten Textverarbeitung für Innovationsförderung")
    st.write(
        """
        Dieses System unterstützt die IFB Hamburg bei der automatisierten Prüfung und Bewertung von Förderanträgen
        im PROFI-Programm. Durch den Einsatz lokaler Large Language Models (LLMs) werden Anträge analysiert,
        Kriterien geprüft und Bewertungen erstellt – vollständig offline und datenschutzkonform.
        """
    )

    st.header("Funktionen")
    st.markdown(
        """
        • Automatische Dokumentenanalyse (PDF, DOCX, XLSX)
        • Prüfung von Förderkriterien
        • Strukturierte Bewertung nach IFB-Standards
        • Generierung von Prüfberichten und Checklisten
        • 100% lokale Verarbeitung für maximale Datensicherheit
        """
    )

    st.header("Technologie")
    st.write(
        """
        Basierend auf LM Studio mit lokalen Qwen-Modellen, ChromaDB für Vektorspeicherung und Python für die Verarbeitung.
        """
    )

    st.success("System bereit – Wähle links eine Seite aus, um fortzufahren.")

    st.caption("Alle Seitenwechsel und Interaktionen werden im Terminal protokolliert.")


if __name__ == "__main__":
    main()
