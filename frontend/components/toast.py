"""Lightweight toast helpers rendered via markdown blocks."""
from __future__ import annotations

from typing import Literal

import streamlit as st

Tone = Literal["info", "success", "warning", "error"]


_TONE_STYLES = {
    "info": ("#E8F1FF", "#175cd3", "i"),
    "success": ("#E6F4EA", "#10713F", "+"),
    "warning": ("#FFF4E5", "#B54708", "!"),
    "error": ("#FEE6E6", "#B42318", "x"),
}


def show_toast(message: str, tone: Tone = "info", icon: str | None = None) -> None:
    """Render a consistent toast-like message area."""

    background, color, default_icon = _TONE_STYLES.get(tone, _TONE_STYLES["info"])
    icon = icon or default_icon
    st.markdown(
        f"""<div style="background:{background};color:{color};padding:0.6rem 0.9rem;
        border-radius:6px;margin-bottom:0.4rem;font-size:0.9rem;">
        <span style="margin-right:0.4rem;">{icon}</span>{message}
        </div>""",
        unsafe_allow_html=True,
    )
