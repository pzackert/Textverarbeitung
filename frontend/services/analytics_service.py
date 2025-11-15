"""Analytics helpers for dashboard visualizations (heatmap, stats, etc.)."""
from __future__ import annotations

from datetime import date, timedelta
from typing import List, TypedDict


class HeatmapEntry(TypedDict):
    day: str
    value: int


def _daterange(start: date, end: date) -> List[date]:
    days: List[date] = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def get_daily_stats(start: date, end: date, max_projects: int = 50) -> List[HeatmapEntry]:
    """Return mock daily stats limited to a safe project count for the MVP."""
    days = _daterange(start, end)
    budget = max(1, min(max_projects, 50))
    data: List[HeatmapEntry] = []
    for index, day in enumerate(days):
        value = (index % budget) % 6  # deterministic pseudo data
        data.append({"day": day.isoformat(), "value": value})
    return data
