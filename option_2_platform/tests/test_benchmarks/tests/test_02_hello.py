"""Test 2: Hello World (Baseline)."""
import pytest
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from benchmarks.utils.config import ModelConfig
from benchmarks.utils.llm_client import LLMClient


class TestHelloWorld:
    """Test basic prompt response (Hello World baseline)."""

    @pytest.mark.parametrize(
        "model_config",
        [
            ModelConfig(name="qwen2.5:0.5b", backend="ollama", enabled=True),
            ModelConfig(name="qwen2.5:7b", backend="ollama", enabled=True),
        ],
    )
    def test_hello_world(self, model_config):
        """
        Test: Query model with 'Say hello!' and validate response.

        Validation:
        - Response contains 'hello' (case-insensitive)

        Metrics:
        - response_time_s: Time to generate response
        - tokens_per_sec: Generation speed
        """
        client = LLMClient(model_config.name)

        # Check availability
        available = client.check_availability()
        if not available:
            pytest.skip(f"Model {model_config.name} not available")

        # Query
        prompt = "Say hello!"
        result = client.query(prompt, temperature=0.7, max_tokens=100)

        # Assertions
        assert result["success"], "Query failed"
        assert result["response"], "Response is empty"

        # Validate response contains 'hello' (case-insensitive)
        response_lower = result["response"].lower()
        assert "hello" in response_lower or "hi" in response_lower, (
            f"Response doesn't contain greeting. Got: {result['response']}"
        )

        # Check metrics
        metrics = result["metrics"]
        assert metrics is not None, "Metrics not collected"
        assert metrics.response_time_s > 0, "Response time should be positive"

        # Store for result collection
        TestHelloWorld.last_metrics = metrics
        TestHelloWorld.last_model = model_config.name
        TestHelloWorld.last_response = result["response"]
