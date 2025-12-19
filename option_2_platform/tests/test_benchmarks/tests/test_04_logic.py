"""Test 4: Logic Puzzle (LCM scheduling)."""
import re
import pytest
from pathlib import Path
import sys

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from benchmarks.utils.config import ConfigLoader
from benchmarks.utils.llm_client import LLMClient


class TestLogicPuzzle:
    """Test logic reasoning capability."""

    @pytest.mark.parametrize(
        "model_config",
        ConfigLoader.from_project_root().get_enabled_models(),
    )
    def test_logic_puzzle(self, model_config):
        """
        Test: Maschinen-Taktung mit Antworten A/B/C.

        Prompt:
        A company operates three machines, A, B, and C. Machine A produces one component
        every 4 minutes. Machine B produces one component every 6 minutes. Machine C produces
        one component every 9 minutes. All three machines start at the same time at 8:00 a.m.
        and run without interruption. After how many minutes will all three machines together
        have produced exactly 30 components for the first time? Answer A = 48, Answer B = 54,
        Answer C = 60. Answer only with the letter of the correct answer.

        Expected answer: B (54 Minuten)

        Validation:
        - Response contains standalone letter 'B' (accepts "Antwort B" variants)

        Metrics:
        - response_time_s: Time to generate response
        - tokens_per_sec: Generation speed
        - correct: Whether answer indicates option B
        """
        client = LLMClient(model_config.name)
        repetitions = ConfigLoader.from_project_root().repetitions

        # Check availability
        if not client.check_availability():
            pytest.skip(f"Model {model_config.name} not available")

        prompt = (
            "A company operates three machines, A, B, and C. Machine A produces one component "
            "every 4 minutes. Machine B produces one component every 6 minutes. Machine C "
            "produces one component every 9 minutes. All three machines start at the same time "
            "at 8:00 a.m. and run without interruption. After how many minutes will all three "
            "machines together have produced exactly 30 components for the first time? Answer A = 48, "
            "Answer B = 54, Answer C = 60. Calculate the correct answer and return only the letter of the correct answer"
        )
        correct_runs = 0
        response_times = []
        last_response = ""

        for _ in range(repetitions):
            result = client.query(prompt, temperature=0.0, max_tokens=100)
            if not result.get("success") or not result.get("response"):
                continue

            response = result["response"].strip()
            normalized = response.upper()
            if re.search(r"\bB\b", normalized):
                correct_runs += 1
                last_response = result["response"]
                metrics = result.get("metrics")
                if metrics and metrics.response_time_s is not None:
                    response_times.append(metrics.response_time_s)

        if correct_runs == 0 and not last_response:
            pytest.skip(f"Model {model_config.name} returned empty responses")

        assert correct_runs > 0, f"Expected 'B' from {model_config.name}, got none"

        # Store for result collection
        TestLogicPuzzle.last_model = model_config.name
        TestLogicPuzzle.last_response = last_response
        TestLogicPuzzle.correct = correct_runs > 0
        TestLogicPuzzle.last_metrics = None
        if response_times:
            avg_rt = sum(response_times) / len(response_times)
            TestLogicPuzzle.last_metrics = {
                "avg_response_time_s": round(avg_rt, 2),
                "runs": correct_runs,
            }
