"""Shared fixtures for benchmark tests."""
from __future__ import annotations

import sys
from pathlib import Path
from typing import List

import pytest

# Ensure src and benchmark utilities are importable
ROOT = Path(__file__).parent.parent
SRC_PATH = ROOT.parent / "src"
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from benchmarks.utils.config import ConfigLoader
from benchmarks.utils.rag_helper import RAGBenchmarkHelper


@pytest.fixture(scope="session")
def benchmark_config():
    """Load benchmark configuration once per session."""
    return ConfigLoader.from_project_root()


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return Path(__file__).parent / "data"


@pytest.fixture(scope="session")
def rag_helper(data_dir: Path) -> RAGBenchmarkHelper:
    helper = RAGBenchmarkHelper(data_dir=data_dir, collection_name="benchmarks_suite")
    helper.clear_vectorstore()
    yield helper
    helper.clear_vectorstore()


@pytest.fixture(scope="session")
def all_documents(data_dir: Path) -> List[str]:
    return [str(p) for p in sorted(data_dir.iterdir()) if p.is_file()]


@pytest.fixture(scope="session")
def ingested_all(rag_helper: RAGBenchmarkHelper, all_documents: List[str]):
    """Ingest all benchmark documents once for RAG-based tests."""
    metrics = rag_helper.ingest_documents(all_documents)
    return metrics
