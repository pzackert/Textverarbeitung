"""Test orchestrator - Main benchmark suite runner."""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any
import logging
import sys
import platform

# Add paths
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

from benchmarks.utils.config import ConfigLoader
from benchmarks.utils.llm_client import LLMClient

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)


class BenchmarkOrchestrator:
    """Orchestrates benchmark test suite."""

    def __init__(self, config_path: Path = None):
        """Initialize orchestrator with configuration."""
        if config_path is None:
            config_path = (
                Path(__file__).parent / "config" / "models.toml"
            )
        self.config = ConfigLoader(config_path).load()
        self.results = []
        self.run_metadata = {}

    def get_system_info(self) -> Dict[str, Any]:
        """Collect system information."""
        try:
            import psutil

            return {
                "os": platform.system(),
                "platform": platform.platform(),
                "cpu_count": psutil.cpu_count(),
                "cpu_freq": f"{psutil.cpu_freq().current:.0f} MHz"
                if psutil.cpu_freq()
                else "Unknown",
                "total_ram_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            }
        except Exception as e:
            logger.warning(f"Failed to collect system info: {e}")
            return {
                "os": platform.system(),
                "error": str(e),
            }

    def run_test_01_loading(
        self, model_name: str
    ) -> Dict[str, Any]:
        """Run Test 1: Model Loading."""
        logger.info(f"  [Test 1/4] Model Loading - {model_name}")
        client = LLMClient(model_name)

        if not client.check_availability():
            logger.warning(f"    Model {model_name} not available, skipping")
            return None

        try:
            metrics = client.load_model()
            return {
                "model": model_name,
                "test": "01_model_loading",
                "passed": metrics["success"],
                "cold_start_time_s": metrics["cold_start_time_s"],
                "warmup_time_s": metrics["warmup_time_s"],
                "ram_used_mb": metrics["ram_used_mb"],
            }
        except Exception as e:
            logger.error(f"Test 1 failed for {model_name}: {e}")
            return {
                "model": model_name,
                "test": "01_model_loading",
                "passed": False,
                "error": str(e),
            }

    def run_test_02_hello(self, model_name: str) -> Dict[str, Any]:
        """Run Test 2: Hello World (run multiple times for statistics)."""
        logger.info(f"  [Test 2/4] Hello World - {model_name}")
        client = LLMClient(model_name)

        if not client.check_availability():
            return None

        attempts = []
        prompt = "Say hello!"

        for i in range(self.config.repetitions):
            try:
                result = client.query(prompt, temperature=0.7, max_tokens=100)
                if result["success"]:
                    metrics = result["metrics"]
                    attempt = {
                        "response_time_s": metrics.response_time_s,
                        "tokens_per_sec": metrics.tokens_per_sec,
                        "answer": result["response"].strip()[:50],  # First 50 chars
                    }
                    attempts.append(attempt)
                    logger.info(
                        f"    Attempt {i+1}/{self.config.repetitions}: "
                        f"{metrics.response_time_s}s ({metrics.tokens_per_sec} tok/s)"
                    )
            except Exception as e:
                logger.error(f"Attempt {i+1} failed: {e}")

        if not attempts:
            return {
                "model": model_name,
                "test": "02_hello_world",
                "passed": False,
            }

        # Calculate statistics
        avg_time = sum(a["response_time_s"] for a in attempts) / len(attempts)
        avg_tokens = (
            sum(a["tokens_per_sec"] for a in attempts if a["tokens_per_sec"])
            / len([a for a in attempts if a["tokens_per_sec"]])
        )

        return {
            "model": model_name,
            "test": "02_hello_world",
            "passed": True,
            "attempts": attempts,
            "avg_response_time_s": round(avg_time, 2),
            "avg_tokens_per_sec": round(avg_tokens, 1),
        }

    def run_test_03_math(self, model_name: str) -> Dict[str, Any]:
        """Run Test 3: Math Reasoning (multiple attempts)."""
        logger.info(f"  [Test 3/4] Math Reasoning - {model_name}")
        client = LLMClient(model_name)

        if not client.check_availability():
            return None

        attempts = []
        prompt = "Calculate: 4 + 8 × 7. Only give the number."

        for i in range(self.config.repetitions):
            try:
                result = client.query(prompt, temperature=0.0, max_tokens=50)
                if result["success"]:
                    metrics = result["metrics"]
                    response = result["response"].strip()
                    correct = "60" in response

                    attempt = {
                        "response_time_s": metrics.response_time_s,
                        "answer": response[:50],
                        "correct": correct,
                    }
                    attempts.append(attempt)
                    logger.info(
                        f"    Attempt {i+1}/{self.config.repetitions}: "
                        f"{metrics.response_time_s}s - {response} {'✓' if correct else '✗'}"
                    )
            except Exception as e:
                logger.error(f"Attempt {i+1} failed: {e}")

        if not attempts:
            return {
                "model": model_name,
                "test": "03_math",
                "passed": False,
            }

        # Calculate statistics
        avg_time = sum(a["response_time_s"] for a in attempts) / len(attempts)
        correct_count = sum(1 for a in attempts if a["correct"])
        accuracy = correct_count / len(attempts)

        return {
            "model": model_name,
            "test": "03_math",
            "passed": accuracy > 0,
            "attempts": attempts,
            "avg_response_time_s": round(avg_time, 2),
            "accuracy": round(accuracy, 2),
        }

    def run_test_04_logic(self, model_name: str) -> Dict[str, Any]:
        """Run Test 4: Logic Puzzle (multiple attempts)."""
        logger.info(f"  [Test 4/4] Logic Puzzle - {model_name}")
        client = LLMClient(model_name)

        if not client.check_availability():
            return None

        attempts = []
        prompt = "Three apples cost 6 euros. How much does one apple cost?"

        for i in range(self.config.repetitions):
            try:
                result = client.query(prompt, temperature=0.0, max_tokens=100)
                if result["success"]:
                    metrics = result["metrics"]
                    response = result["response"].strip()
                    correct = "2" in response

                    attempt = {
                        "response_time_s": metrics.response_time_s,
                        "answer": response[:100],
                        "correct": correct,
                    }
                    attempts.append(attempt)
                    logger.info(
                        f"    Attempt {i+1}/{self.config.repetitions}: "
                        f"{metrics.response_time_s}s {'✓' if correct else '✗'}"
                    )
            except Exception as e:
                logger.error(f"Attempt {i+1} failed: {e}")

        if not attempts:
            return {
                "model": model_name,
                "test": "04_logic",
                "passed": False,
            }

        # Calculate statistics
        avg_time = sum(a["response_time_s"] for a in attempts) / len(attempts)
        correct_count = sum(1 for a in attempts if a["correct"])
        accuracy = correct_count / len(attempts)

        return {
            "model": model_name,
            "test": "04_logic",
            "passed": accuracy > 0,
            "attempts": attempts,
            "avg_response_time_s": round(avg_time, 2),
            "accuracy": round(accuracy, 2),
        }

    def run(self) -> Dict[str, Any]:
        """Run all tests for all configured models."""
        enabled_models = self.config.get_enabled_models()

        # Print header
        print("\n" + "=" * 70)
        print("  LLM BENCHMARK - Test Suite".center(70))
        print("=" * 70 + "\n")

        print(f"Configuration:")
        print(f"  - Models: {len(enabled_models)} ({', '.join(m.name for m in enabled_models)})")
        print(f"  - Tests: 4")
        print(f"  - Repetitions: {self.config.repetitions}")
        print(f"  - Warmup: {self.config.warmup}\n")

        # Prepare metadata
        timestamp = datetime.utcnow().isoformat() + "Z"
        self.run_metadata = {
            "timestamp": timestamp,
            "system": self.get_system_info(),
            "config": {
                "repetitions": self.config.repetitions,
                "warmup": self.config.warmup,
            },
        }

        # Run tests for each model
        for idx, model in enumerate(enabled_models, 1):
            print(f"[{idx}/{len(enabled_models)}] Model: {model.name} ({model.backend})")
            print("-" * 70)

            # Test 1: Loading
            result = self.run_test_01_loading(model.name)
            if result:
                self.results.append(result)

            # Tests 2-4: Only run if loading succeeded
            if result and result.get("passed"):
                # Test 2: Hello
                result = self.run_test_02_hello(model.name)
                if result:
                    self.results.append(result)

                # Test 3: Math
                result = self.run_test_03_math(model.name)
                if result:
                    self.results.append(result)

                # Test 4: Logic
                result = self.run_test_04_logic(model.name)
                if result:
                    self.results.append(result)

        # Save results
        output_path = self._save_results()
        print("\n" + "=" * 70)
        print(f"Results saved to: {output_path}".center(70))
        print("=" * 70 + "\n")

        return {
            "run_metadata": self.run_metadata,
            "results": self.results,
        }

    def _save_results(self) -> Path:
        """Save results to JSON file."""
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)

        # Generate filename from timestamp
        timestamp_str = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        output_file = results_dir / f"run_{timestamp_str}.json"

        output_data = {
            "run_metadata": self.run_metadata,
            "results": self.results,
        }

        with open(output_file, "w") as f:
            json.dump(output_data, f, indent=2)

        logger.info(f"Results saved to {output_file}")
        return output_file


def main():
    """Main entry point for benchmark suite."""
    orchestrator = BenchmarkOrchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()
