"""Test 7: Steckbrief information extraction via RAG."""
from __future__ import annotations

from pathlib import Path
import sys

import pytest

# Ensure src on path
ROOT = Path(__file__).parent.parent.parent.parent / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.utils.config import ConfigLoader
from benchmarks.utils.validation import validate_any_of


class TestRAGSteckbrief:
    """Query Steckbrief details using RAG."""

    @pytest.mark.parametrize(
        "model_config",
        ConfigLoader.from_project_root().get_enabled_models(),
    )
    def test_rag_steckbrief(self, model_config, rag_helper, ingested_all):
        # Ensure documents ingested (fixture ingested_all triggers ingestion)
        _ = ingested_all

        queries = [
            (
                "Wer ist der Betreuer der Unternehmung?",
                ["appel", "kristoffer"],
            ),
            (
                "Wer ist der Auftraggeber?",
                ["ifb", "auftraggeber", "hamburg"],
            ),
        ]

        answers = 0
        for question, expected_terms in queries:
            result = rag_helper.query(
                question,
                model_name=model_config.name,
                temperature=0.0,
                max_tokens=256,
                context_length=4096,
                top_k=6,
            )
            if not result.get("success"):
                continue
            answer = result.get("answer", "")
            if validate_any_of(expected_terms, answer):
                answers += 1

        assert answers >= 1, "Expected at least one correct Steckbrief answer"

        self.last_result = {
            "answers_correct": answers,
            "total_queries": len(queries),
        }
