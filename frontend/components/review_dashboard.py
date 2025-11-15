"""Dashboard overview for the command center."""
from __future__ import annotations

from typing import Iterable, Optional, Sequence, TYPE_CHECKING

import streamlit as st

from frontend.components import heatmap
from frontend.services import project_service

if TYPE_CHECKING:  # pragma: no cover
    from frontend.services.project_service import ProjectRecord


def _project_stats(records: Sequence[project_service.ProjectRecord]) -> dict[str, int]:
    stats = {
        "total": len(records),
        "uploading": sum(1 for rec in records if rec.status in {"uploading", "documents"}),
        "checked": sum(1 for rec in records if rec.status in {"checked", "completed"}),
        "ready": sum(1 for rec in records if rec.status == "uploaded"),
    }
    return stats


def _detail_table(record: Optional[project_service.ProjectRecord]) -> None:
    if not record:
        st.info("Noch kein Projekt ausgewaehlt.")
        return
    st.write(
        {
            "ID": record.id,
            "Antragsteller": record.applicant or "n/a",
            "Modul": record.modul or "n/a",
            "Projektart": record.project_type or "n/a",
            "Letzter Upload": record.last_upload_at or "-",
            "Letzte Pruefung": record.last_check_at or "-",
            "Status": record.status_label,
        }
    )


def render_review_dashboard(
    records: Sequence[project_service.ProjectRecord],
    active_record: Optional[project_service.ProjectRecord],
    heatmap_data: Iterable[dict[str, int | str]],
) -> None:
    """Render overview cards, how-to guide, and current project details."""

    stats = _project_stats(records)
    st.markdown("### Command Center Uebersicht")
    col_a, col_b, col_c, col_d = st.columns(4)
    col_a.metric("Projekte", stats["total"])
    col_b.metric("Upload offen", stats["uploading"])
    col_c.metric("Bereit zur Pruefung", stats["ready"])
    col_d.metric("Abgeschlossen", stats["checked"])

    guide_col, detail_col = st.columns([2, 1])
    with guide_col:
        with st.expander("So funktioniert es", expanded=True):
            st.markdown(
                """
                1. Dokumente hochladen (Drag & Drop pro Kategorie).
                2. KI-gestuetzte Pruefung starten, sobald Pflichtdokumente vorhanden sind.
                3. Ergebnisse validieren, Notizen erfassen und Folgeaktionen anstossen.
                """
            )
        heatmap.render_heatmap(heatmap_data, "Letzte Aktivitaeten")
    with detail_col:
        st.markdown("#### Projektkontext")
        _detail_table(active_record)
        st.markdown("#### Vermerke")
        st.text_area(
            "Interne Notizen",
            value="",
            height=120,
            placeholder="Kurze Stichpunkte fuer das Team...",
            key="notes_area",
        )
