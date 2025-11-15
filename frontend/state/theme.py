"""Theme tokens derived from Streamlit settings."""
from __future__ import annotations

from dataclasses import dataclass

import streamlit as st


@dataclass(frozen=True)
class ThemeTokens:
    primary: str
    secondary: str
    text: str
    background: str
def _safe_option(key: str) -> str | None:
    try:
        return st.get_option(key)
    except Exception:  # pragma: no cover - streamlit guards
        return None


def get_tokens() -> ThemeTokens:
    return ThemeTokens(
        primary=_safe_option("theme.primaryColor") or "#005ca9",
        secondary=_safe_option("theme.secondaryBackgroundColor") or "#f5f5f5",
        text=_safe_option("theme.textColor") or "#262730",
        background=_safe_option("theme.backgroundColor") or "#ffffff",
    )
