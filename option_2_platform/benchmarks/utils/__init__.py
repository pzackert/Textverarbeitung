"""Re-export benchmark utility modules from tests/test_benchmarks."""
from importlib import import_module
from pathlib import Path
import sys

TESTS_ROOT = Path(__file__).resolve().parents[2] / "tests"
if str(TESTS_ROOT) not in sys.path:
    sys.path.insert(0, str(TESTS_ROOT))

config = import_module("test_benchmarks.utils.config")
llm_client = import_module("test_benchmarks.utils.llm_client")
rag_helper = import_module("test_benchmarks.utils.rag_helper")
validation = import_module("test_benchmarks.utils.validation")

__all__ = ["config", "llm_client", "rag_helper", "validation"]
