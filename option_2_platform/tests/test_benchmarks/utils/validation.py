"""Shared validation helpers for benchmark tests."""
from __future__ import annotations

from typing import Iterable


def validate_fuzzy(expected: str, actual: str) -> bool:
    """Case-insensitive contains check."""
    return expected.lower() in actual.lower()


def validate_any_of(expected_list: Iterable[str], actual: str) -> bool:
    """Return True if any of the expected terms is contained (case-insensitive)."""
    lower = actual.lower()
    return any(term.lower() in lower for term in expected_list)


def validate_length(text: str, max_chars: int, tolerance: float = 0.1) -> bool:
    """Check length with tolerance (max * (1 + tolerance))."""
    return len(text) <= int(max_chars * (1 + tolerance))


def validate_word_count(text: str, min_words: int) -> bool:
    """Check minimum word count."""
    return len(text.split()) >= min_words
