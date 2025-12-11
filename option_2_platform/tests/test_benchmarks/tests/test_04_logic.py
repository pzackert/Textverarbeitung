"""Test 4: Logic Puzzle (Easy)."""
import pytest
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from benchmarks.utils.config import ModelConfig
from benchmarks.utils.llm_client import LLMClient


class TestLogicPuzzle:
    """Test logic reasoning capability."""

    @pytest.mark.parametrize(
        "model_config",
        [
            ModelConfig(name="qwen2.5:0.5b", backend="ollama", enabled=True),
            ModelConfig(name="qwen2.5:7b", backend="ollama", enabled=True),
        ],
    )
    def test_logic_puzzle(self, model_config):
        """
        Test: Logic puzzle - Three apples cost 6 euros. How much does one cost?

        Expected answer: 2 (euros)

        Validation:
        - Response contains '2' in the context of euros/cost

        Metrics:
        - response_time_s: Time to generate response
        - tokens_per_sec: Generation speed
        - correct: Whether answer indicates '2 euros'
        """
        client = LLMClient(model_config.name)

        # Check availability
        available = client.check_availability()
        if not available:
            pytest.skip(f"Model {model_config.name} not available")

        # Query
        prompt = "Three apples cost 6 euros. How much does one apple cost?"
        result = client.query(prompt, temperature=0.0, max_tokens=100)

        # Assertions
        assert result["success"], "Query failed"
        assert result["response"], "Response is empty"

        # Validate answer indicates 2 euros
        response = result["response"].strip().lower()
        correct = "2" in response

        # Store for result collection
        TestLogicPuzzle.last_metrics = result["metrics"]
        TestLogicPuzzle.last_model = model_config.name
        TestLogicPuzzle.last_response = response
        TestLogicPuzzle.correct = correct

        # Assert the test passes (correct answer)
        assert correct, f"Expected '2', got '{response}'"
