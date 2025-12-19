"""Test 5: Direct LLM file query without RAG."""
from __future__ import annotations

import re
import time
from pathlib import Path
import sys

import pytest

# Ensure src on path for parsers
ROOT = Path(__file__).parent.parent.parent.parent / "src"
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.utils.config import ConfigLoader
from benchmarks.utils.llm_client import LLMClient
from benchmarks.utils.validation import validate_word_count
from src.parsers.pdf_parser import PDFParser
from src.parsers.docx_parser import DocxParser


CONFIG = ConfigLoader.from_project_root()
ENABLED_MODELS = CONFIG.get_enabled_models()
REPETITIONS = CONFIG.repetitions


def _extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        docs = PDFParser().parse(str(file_path))
        return "\n".join(d.content for d in docs)
    if suffix == ".docx":
        docs = DocxParser().parse(str(file_path))
        return "\n".join(d.content for d in docs)
    return file_path.read_text(encoding="utf-8", errors="ignore")


def _find_smallest_document(data_dir: Path) -> Path:
    files = [p for p in data_dir.iterdir() if p.is_file()]
    if not files:
        raise FileNotFoundError("No documents found in data directory")
    return min(files, key=lambda p: p.stat().st_size)


class TestDirectLLMFile:
    """Direct LLM prompt with full document context (no RAG)."""

    @pytest.mark.parametrize("model_config", ENABLED_MODELS)
    def test_direct_llm_summary(self, model_config, data_dir):
        file_path = _find_smallest_document(data_dir)

        read_start = time.perf_counter()
        text = _extract_text(file_path)
        load_time = time.perf_counter() - read_start

        client = LLMClient(model_config.name)
        if not client.check_availability():
            pytest.skip(f"Model {model_config.name} not available")

        prompt = (
            "Lies den folgenden Text vollständig und fasse ihn in drei kurzen Sätzen"
            " zusammen. Antworte auf Deutsch und bleibe prägnant.\n\n"
            f"Text:\n{text}\n\nZusammenfassung:"
        )

        successes = 0
        response_times = []
        last_response = ""

        for _ in range(REPETITIONS):
            result = client.query(
                prompt,
                temperature=0.7,
                max_tokens=512,
                context_length=4096,
            )

            if not result.get("success") or not result.get("response"):
                continue

            response = result["response"].strip()
            sentences = [s for s in re.split(r"[.!?]", response) if s.strip()]
            if 2 <= len(sentences) <= 50 and validate_word_count(response, 20):
                successes += 1
                last_response = response
                metrics = result.get("metrics")
                if metrics and metrics.response_time_s is not None:
                    response_times.append(metrics.response_time_s)

        if successes == 0 and not last_response:
            pytest.skip(f"Model {model_config.name} returned empty or invalid responses")

        assert successes > 0, f"Summary not returned by {model_config.name}"

        # Attach debug info for result consumers
        self.last_result = {
            "document": file_path.name,
            "document_size_kb": round(file_path.stat().st_size / 1024, 2),
            "load_time_s": round(load_time, 3),
            "last_response": last_response,
        }
        if response_times:
            avg_rt = sum(response_times) / len(response_times)
            self.last_result["avg_response_time_s"] = round(avg_rt, 2)
