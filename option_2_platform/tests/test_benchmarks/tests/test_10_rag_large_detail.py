"""Test 10: Detailed query against large document using RAG."""
from __future__ import annotations

from pathlib import Path
import sys

import pytest

# Ensure src on path
ROOT = Path(__file__).parent.parent.parent.parent / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.utils.config import ConfigLoader
from benchmarks.utils.validation import validate_any_of, validate_word_count


KEYWORDS = ["integration", "web browsing", "browser", "enhancing"]
ERROR_TERMS = ["cannot", "unable", "keine information", "not found"]


class TestRAGLargeDetail:
    """Detailed technical retrieval from qbusiness-ug.pdf."""

    @pytest.mark.parametrize(
        "model_config",
        ConfigLoader.from_project_root().get_enabled_models(),
    )
    @pytest.mark.timeout(300)
    def test_large_detail_query(self, model_config, rag_helper):
        large_doc = Path(__file__).parent.parent / "data" / "qbusiness-ug.pdf"
        if not large_doc.exists():
            pytest.skip("Large document not available")

        config = ConfigLoader.from_project_root()
        contexts = [c for c in config.context_length if c >= 16384] or [max(config.context_length)]

        rag_helper.clear_vectorstore()
        ingest = rag_helper.ingest_documents([str(large_doc)])
        assert ingest["success"], "Ingestion failed for large document"

        passed = False
        used_ctx = None
        answer_text = ""

        for ctx in contexts:
            result = rag_helper.query(
                "Wie funktioniert die Integration von 'Enhancing Web Browsing mit Q-Business'?"
                " Erkläre die technische Integration.",
                model_name=model_config.name,
                temperature=0.0,
                max_tokens=512,
                context_length=ctx,
                top_k=12,
            )
            if not result.get("success"):
                continue

            answer = result.get("answer", "")
            if not answer:
                continue

            if not validate_any_of(KEYWORDS, answer):
                continue
            if any(term in answer.lower() for term in ERROR_TERMS):
                continue
            if not validate_word_count(answer, 50):
                continue

            passed = True
            used_ctx = ctx
            answer_text = answer
            break

        assert passed, "No detailed answer produced within context limits"

        self.last_result = {
            "context_length_used": used_ctx,
            "response_words": len(answer_text.split()),
        }
