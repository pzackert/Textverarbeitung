"""Test 3: Math Reasoning (4 + 8 × 7 = 60)."""
import pytest
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from benchmarks.utils.config import ModelConfig
from benchmarks.utils.llm_client import LLMClient


class TestMathReasoning:
    """Test math reasoning capability."""

    @pytest.mark.parametrize(
        "model_config",
        [
            ModelConfig(name="qwen2.5:0.5b", backend="ollama", enabled=True),
            ModelConfig(name="qwen2.5:7b", backend="ollama", enabled=True),
        ],
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

        # Check availability
        available = client.check_availability()
        if not available:
            pytest.skip(f"Model {model_config.name} not available")

        # Query
        prompt = "Calculate: 4 + 8 × 7. Only give the number."
        result = client.query(prompt, temperature=0.0, max_tokens=100)

        # Assertions
        assert result["success"], "Query failed"
        assert result["response"], "Response is empty"

        # Validate answer is 60
        response = result["response"].strip()
        correct = "60" in response

        # Store for result collection
        TestMathReasoning.last_metrics = result["metrics"]
        TestMathReasoning.last_model = model_config.name
        TestMathReasoning.last_response = response
        TestMathReasoning.correct = correct

        # Assert the test passes (correct answer)
        assert correct, f"Expected '60', got '{response}'"
