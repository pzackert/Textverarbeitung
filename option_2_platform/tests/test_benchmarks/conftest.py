"""Shared fixtures for benchmark tests."""
from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import List

import pytest

# Skip benchmarks unless explicitly enabled (heavy, require local models)
RUN_BENCH = bool(os.getenv("RUN_BENCHMARK_TESTS"))
if not RUN_BENCH:
    pytestmark = pytest.mark.skip(reason="Benchmarks disabled; set RUN_BENCHMARK_TESTS=1 to run")

def pytest_ignore_collect(collection_path, config):
    if "test_benchmarks" in str(collection_path) and not RUN_BENCH:
        return True

# Ensure src and benchmark utilities are importable
ROOT = Path(__file__).parent.parent
SRC_PATH = ROOT.parent / "src"
THIS_DIR = Path(__file__).parent
if str(THIS_DIR) not in sys.path:
    sys.path.insert(0, str(THIS_DIR))
if str(SRC_PATH) not in sys.path:
    sys.path.insert(0, str(SRC_PATH))
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from utils.config import ConfigLoader
from utils.rag_helper import RAGBenchmarkHelper


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
