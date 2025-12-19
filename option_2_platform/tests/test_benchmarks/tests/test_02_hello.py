"""Test 2: Hello World (Baseline)."""
import pytest
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from benchmarks.utils.config import ConfigLoader, ModelConfig
from benchmarks.utils.llm_client import LLMClient


class TestHelloWorld:
    """Test basic prompt response (Hello World baseline)."""

    @pytest.mark.parametrize(
        "model_config",
        ConfigLoader.from_project_root().get_enabled_models(),
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
        repetitions = ConfigLoader.from_project_root().repetitions

        # Check availability
        if not client.check_availability():
            pytest.skip(f"Model {model_config.name} not available")

        prompt = "Say hello!"
        successes = 0
        response_times = []
        last_response = ""

        for _ in range(repetitions):
            result = client.query(prompt, temperature=0.7, max_tokens=100)
            if not result.get("success") or not result.get("response"):
                continue
            response_lower = result["response"].lower()
            if "hello" in response_lower or "hi" in response_lower:
                successes += 1
                last_response = result["response"]
                metrics = result.get("metrics")
                if metrics and metrics.response_time_s is not None:
                    response_times.append(metrics.response_time_s)

        assert successes > 0, f"Greeting not returned by {model_config.name}"

        # Store for result collection
        TestHelloWorld.last_model = model_config.name
        TestHelloWorld.last_response = last_response
        TestHelloWorld.last_metrics = None
        if response_times:
            avg_rt = sum(response_times) / len(response_times)
            TestHelloWorld.last_metrics = TestHelloWorld.last_metrics or {}
            TestHelloWorld.last_metrics = {
                "avg_response_time_s": round(avg_rt, 2),
                "runs": successes,
            }
