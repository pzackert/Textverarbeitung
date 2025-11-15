"""Header component for the IFB PROFI Streamlit app."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Optional, TYPE_CHECKING

import streamlit as st

from frontend.state import session_keys, theme

if TYPE_CHECKING:  # pragma: no cover - typing only
    from frontend.services.project_service import ProjectRecord


def render_header(
    stats: Dict[str, int | str],
    active_record: Optional["ProjectRecord"],
) -> None:
    """Render the top header with logo placeholder and settings."""

    session_keys.ensure_defaults()
    tokens = theme.get_tokens()
    header_left, header_center, header_right = st.columns([1.2, 2.6, 1.2])

    with header_left:
        st.markdown(
            """
            <div style="font-weight:600;font-size:1.2rem;">
            IFB&nbsp;PROFI
            </div>
            <div style="font-size:0.85rem;color:#6b7280;">
            Realtime Command Center
            </div>
            """,
            unsafe_allow_html=True,
        )
        current_name = active_record.name if active_record else "-"
        st.caption(f"Aktives Projekt: {current_name}")

    with header_center:
        st.markdown(
            f"""
            <div style="text-align:center">
                <h2 style="margin-bottom:0.2rem;">KI-Antragspruefung</h2>
                <p style="margin:0;color:{tokens.text};">Status-Overview und Next Actions</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        sub_col_a, sub_col_b, sub_col_c = st.columns(3)
        sub_col_a.metric("Projekte", stats.get("total", 0))
        sub_col_b.metric("Bereit", stats.get("ready", 0))
        sub_col_c.metric("Abgeschlossen", stats.get("checked", 0))

    with header_right:
        last_refresh = stats.get("refreshed_at") or datetime.now().strftime("%H:%M:%S")
        st.caption(f"Stand: {last_refresh}")
        with st.expander("Settings"):
            st.toggle("LLM aktiv", value=True, disabled=True)
            st.toggle("6 Kriterien", value=True, disabled=True)
            st.selectbox("Theme", ["Automatisch", "Hell", "Dunkel"], index=0, disabled=True)
