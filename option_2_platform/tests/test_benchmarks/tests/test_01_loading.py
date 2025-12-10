"""Test 1: Model Loading (Cold Start + Warm-up)."""
import pytest
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from benchmarks.utils.config import ConfigLoader, ModelConfig
from benchmarks.utils.llm_client import LLMClient


@pytest.fixture
def config():
    """Load benchmark configuration."""
    return ConfigLoader.from_project_root()


@pytest.fixture
def model_config(config):
    """Parametrize over all enabled models from config."""
    return pytest.mark.parametrize(
        "model_config",
        config.get_enabled_models(),
    )


class TestModelLoading:
    """Test model loading with metrics collection."""

    @pytest.mark.parametrize(
        "model_config",
        [
            ModelConfig(name="qwen2.5:0.5b", backend="ollama", enabled=True),
            ModelConfig(name="qwen2.5:7b", backend="ollama", enabled=True),
        ],
    )
    def test_model_loading(self, model_config):
        """
        Test: Load model and measure cold start + warm-up time.

        Measures:
        - cold_start_time_s: Time to first response
        - warmup_time_s: Time to warm-up query
        - ram_used_mb: RAM usage after loading
        - cpu_percent: CPU usage during load
        """
        client = LLMClient(model_config.name)

        # Check availability
        available = client.check_availability()
        if not available:
            pytest.skip(f"Model {model_config.name} not available in Ollama")

        # Load model (warm-up)
        metrics = client.load_model()

        # Assertions
        assert metrics["success"], "Model loading failed"
        assert metrics["warmup_time_s"] > 0, "Warmup time should be measured"
        assert metrics["ram_used_mb"] >= 0, "RAM usage should be non-negative"

        # Store metrics for result collection
        # These will be captured via pytest fixtures or custom hooks
        TestModelLoading.last_metrics = metrics
        TestModelLoading.last_model = model_config.name
