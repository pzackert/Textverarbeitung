"""Result tab rendering for criteria evaluations."""
from __future__ import annotations

import json
from typing import Any, Dict, Optional

import streamlit as st

from frontend.components.toast import show_toast
from frontend.services import project_service

try:  # pragma: no cover - optional deps
    import pandas as pd
except Exception:  # pragma: no cover - fallback path
    pd = None


def _criteria_table(results: Dict[str, Any]) -> None:
    criteria = results.get("criteria") or []
    if not criteria:
        st.info("Noch keine Kriterien ausgewertet.")
        return

    if pd is None:
        st.table(criteria)
        return

    df = pd.DataFrame(criteria)
    st.dataframe(df[["id", "name", "result", "answer"]], hide_index=True, use_container_width=True)


def render_results_view(
    record: Optional[project_service.ProjectRecord],
    results: Optional[Dict[str, Any]],
) -> None:
    """Render KPIs and allow downloading the latest evaluation."""

    if not record:
        st.info("Bitte Projekt auswaehlen, um Ergebnisse anzuzeigen.")
        return

    if not results:
        st.warning("Fuer dieses Projekt liegen noch keine Ergebnisse vor.")
        return

    summary = results.get("summary", {})
    col1, col2, col3 = st.columns(3)
    col1.metric("Gesamtstatus", results.get("overall", "-").upper())
    col2.metric("Bestanden", summary.get("passed", 0))
    col3.metric("Nicht bestanden", summary.get("failed", 0))

    _criteria_table(results)

    st.markdown("#### Folgeaktionen")
    st.button("Export als PDF (Stub)", disabled=True, use_container_width=True)
    payload = json.dumps(results, indent=2)
    st.download_button(
        "Rohdaten herunterladen",
        data=payload,
        file_name=f"{record.id}_results.json",
        mime="application/json",
        use_container_width=True,
    )
    show_toast("Weitere Output-Formate folgen.", tone="info")
