"""Streamlit project detail page with uploads and evaluation results."""
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


LOGGER.info("page_view | {'page': 'projekt'}")

st.set_page_config(page_title="Projekt", layout="wide")
st.title("📁 Projektübersicht")

st.subheader("📤 Dokumente hochladen")
st.write("Bitte lade den vollständigen Antrag sowie die Projektskizze hoch.")

col_antrag, col_skizze = st.columns(2)
with col_antrag:
    st.write("**Projektantrag (DOCX/PDF)**")
    uploaded_antrag = st.file_uploader(
        "Projektantrag auswählen",
        key="upload_antrag",
        type=["docx", "pdf"],
    )
with col_skizze:
    st.write("**Projekt-Skizze (DOCX/PDF)**")
    uploaded_skizze = st.file_uploader(
        "Projektskizze auswählen",
        key="upload_skizze",
        type=["docx", "pdf"],
    )

if uploaded_antrag:
    st.success(f"Antrag geladen: {uploaded_antrag.name} ({uploaded_antrag.size / 1024:.1f} KB)")
if uploaded_skizze:
    st.success(f"Skizze geladen: {uploaded_skizze.name} ({uploaded_skizze.size / 1024:.1f} KB)")

st.divider()

st.subheader("✓ Antragskriterien überprüfen")
st.write(
    "Startet die automatische Prüfung aller Förderkriterien basierend auf den hochgeladenen Dokumenten."
)
if st.button("Kriterien jetzt prüfen", use_container_width=True):
    _log_event(
        "criteria_check_triggered",
        antrag=bool(uploaded_antrag),
        skizze=bool(uploaded_skizze),
    )
    st.info("Kriterienprüfung gestartet – Ergebnisse erscheinen unten, sobald verfügbar.")

st.divider()

st.subheader("📊 Prüfungsergebnisse")
criteria_results = [
    {
        "Kriterium": "Innovationsgrad ausreichend",
        "Erfüllt": "Ja",
        "Bewertung": "Projekt weist klare Innovationsbestandteile auf.",
        "Anmerkungen": "LLM validiert gegen Kriterienkatalog.",
    },
    {
        "Kriterium": "Finanzplan vollständig",
        "Erfüllt": "Teilweise",
        "Bewertung": "Teil der Kostenstruktur fehlt.",
        "Anmerkungen": "Nachreichung angefordert.",
    },
    {
        "Kriterium": "Marktpotential nachgewiesen",
        "Erfüllt": "Ja",
        "Bewertung": "Analysen zeigen klares Wachstumspotential.",
        "Anmerkungen": "Risikobewertung positiv.",
    },
    {
        "Kriterium": "Projektteam qualifiziert",
        "Erfüllt": "Ja",
        "Bewertung": "Team verfügt über relevante Expertise.",
        "Anmerkungen": "Referenzen vorhanden.",
    },
    {
        "Kriterium": "Zeitplan realistisch",
        "Erfüllt": "Nein",
        "Bewertung": "Meilensteinplanung unvollständig.",
        "Anmerkungen": "Überarbeitung erforderlich.",
    },
    {
        "Kriterium": "Nachhaltigkeitskonzept",
        "Erfüllt": "Teilweise",
        "Bewertung": "Nachhaltigkeitsziele sind vorhanden, Umsetzung unklar.",
        "Anmerkungen": "Detailplan wird benötigt.",
    },
]

status_colors = {
    "Ja": "✅",
    "Nein": "❌",
    "Teilweise": "⚠️",
}

for result in criteria_results:
    badge = status_colors.get(result["Erfüllt"], "ℹ️")
    st.markdown(
        f"**{badge} {result['Kriterium']}**  \
        **Erfüllt:** {result['Erfüllt']}  \
        **Bewertung:** {result['Bewertung']}  \
        **Anmerkungen:** {result['Anmerkungen']}"
    )
    st.divider()

st.caption("Diese Ergebnisse dienen als Platzhalter für die automatisierte Bewertung.")
