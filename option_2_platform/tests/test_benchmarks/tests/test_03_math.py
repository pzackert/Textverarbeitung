"""Test 3: Math Reasoning (4 + 8 × 7 = 60)."""
import pytest
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from benchmarks.utils.config import ConfigLoader, ModelConfig
from benchmarks.utils.llm_client import LLMClient


class TestMathReasoning:
    """Test math reasoning capability."""

    @pytest.mark.parametrize(
        "model_config",
        ConfigLoader.from_project_root().get_enabled_models(),
    )
    def test_math_reasoning(self, model_config):
        """
        Test: Math problem - 4 + 8 × 7 = ?

        Expected answer: 60

        Validation:
        - Response contains '60'

        Metrics:
        - response_time_s: Time to generate response
        - tokens_per_sec: Generation speed
        - correct: Whether answer matches expected value
        """
        client = LLMClient(model_config.name)
        repetitions = ConfigLoader.from_project_root().repetitions

        if not client.check_availability():
            pytest.skip(f"Model {model_config.name} not available")

        prompt = "Calculate: 4 + 8 × 7. Only give the number."
        correct_runs = 0
        response_times = []
        last_response = ""

        for _ in range(repetitions):
            result = client.query(prompt, temperature=0.0, max_tokens=100)
            if not result.get("success") or not result.get("response"):
                continue
            response = result["response"].strip()
            if "60" in response:
                correct_runs += 1
                last_response = response
                metrics = result.get("metrics")
                if metrics and metrics.response_time_s is not None:
                    response_times.append(metrics.response_time_s)

        assert correct_runs > 0, f"Expected '60' from {model_config.name}, got none"

        # Store for result collection
        TestMathReasoning.last_model = model_config.name
        TestMathReasoning.last_response = last_response
        TestMathReasoning.correct = correct_runs > 0
        TestMathReasoning.last_metrics = None
        if response_times:
            avg_rt = sum(response_times) / len(response_times)
            TestMathReasoning.last_metrics = {
                "avg_response_time_s": round(avg_rt, 2),
                "runs": correct_runs,
            }
