"""Calendar heatmap renderer with graceful fallback."""
from __future__ import annotations

from typing import Iterable

import streamlit as st

try:  # pragma: no cover - optional deps
    import pandas as pd
    import altair as alt
except Exception:  # pragma: no cover - fallback path
    pd = None
    alt = None


def render_heatmap(data: Iterable[dict[str, int | str]], title: str) -> None:
    """Render activity data as GitHub-style calendar using Altair if available."""

    st.markdown(f"#### {title}")
    entries = list(data)
    if not entries:
        st.info("Noch keine Aktivitaet vorhanden.")
        return

    if pd is None or alt is None:
        st.dataframe(entries, use_container_width=True)
        return

    df = pd.DataFrame(entries)
    df["date"] = pd.to_datetime(df["day"], format="%Y-%m-%d")
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["weekday"] = df["date"].dt.weekday

    chart = (
        alt.Chart(df)
        .mark_rect(cornerRadius=3)
        .encode(
            x=alt.X("week:O", title="Kalenderwoche"),
            y=alt.Y("weekday:O", title="Wochentag", sort=[0, 1, 2, 3, 4, 5, 6]),
            color=alt.Color("value:Q", title="Aktivitaet", scale=alt.Scale(scheme="blues")),
            tooltip=["day:T", "value:Q"],
        )
        .properties(height=220)
    )
    st.altair_chart(chart, use_container_width=True)
