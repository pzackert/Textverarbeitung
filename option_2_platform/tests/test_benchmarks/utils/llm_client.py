"""Unified LLM client wrapper for benchmark tests."""
import time
import psutil
import os
from typing import Dict, Any, Optional
from dataclasses import dataclass, asdict
import requests
import logging

logger = logging.getLogger(__name__)


@dataclass
class MetricsData:
    """Metrics collected during LLM query."""
    response_time_s: float
    tokens_per_sec: Optional[float] = None
    ram_used_mb: Optional[float] = None
    cpu_percent: Optional[float] = None


class LLMClient:
    """Unified client for querying LLM models (Ollama backend)."""

    def __init__(self, model_name: str, backend_url: str = "http://localhost:11434"):
        """
        Initialize LLM client.

        Args:
            model_name: Name of the model (e.g., 'qwen2.5:7b')
            backend_url: Base URL of Ollama service
        """
        self.model_name = model_name
        self.backend_url = backend_url.rstrip("/")
        self._process = psutil.Process(os.getpid())
        self._last_metrics: Optional[MetricsData] = None

    def check_availability(self) -> bool:
        """Check if Ollama service and model are available."""
        try:
            # Check if service is running
            response = requests.get(self.backend_url, timeout=5)
            if response.status_code != 200:
                logger.warning(f"Ollama service returned status {response.status_code}")
                return False

            # Check if model is loaded
            url = f"{self.backend_url}/api/tags"
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch model tags")
                return False

            models_data = response.json()
            models = models_data.get("models", [])
            model_names = [m.get("name", "") for m in models]

            # Check for model
            for model_name in model_names:
                if self.model_name in model_name:
                    logger.info(f"Model {self.model_name} is available")
                    return True

            logger.warning(
                f"Model {self.model_name} not found. Available: {model_names}"
            )
            return False

        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to check availability: {e}")
            return False

    def load_model(self) -> Dict[str, Any]:
        """
        Load model (warm-up pull request).
        Measures cold start time if model isn't already loaded.

        Returns:
            Dict with metrics: cold_start_time_s, warmup_time_s, success
        """
        start_time = time.time()
        metrics = {
            "cold_start_time_s": 0,
            "warmup_time_s": 0,
            "ram_used_mb": 0,
            "success": False,
        }

        try:
            # Send a simple generate request to warm up the model
            url = f"{self.backend_url}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": "Hi",
                "stream": False,
                "options": {"num_predict": 1, "temperature": 0.7},
            }

            response = requests.post(url, json=payload, timeout=120)
            elapsed = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                metrics["warmup_time_s"] = round(elapsed, 2)
                metrics["success"] = True
                metrics["ram_used_mb"] = round(self._get_memory_usage(), 1)
                logger.info(
                    f"Model {self.model_name} warmed up in {elapsed:.2f}s"
                )
            else:
                logger.error(f"Failed to load model: {response.status_code}")

        except requests.exceptions.Timeout:
            logger.error(f"Timeout loading model {self.model_name}")
            elapsed = time.time() - start_time
            metrics["warmup_time_s"] = round(elapsed, 2)
        except Exception as e:
            logger.error(f"Error loading model: {e}")

        return metrics

    def query(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
    ) -> Dict[str, Any]:
        """
        Query the LLM and collect metrics.

        Args:
            prompt: Prompt to send to the model
            temperature: Temperature parameter
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with keys: response, metrics (MetricsData)
        """
        start_time = time.time()
        result = {
            "response": "",
            "metrics": None,
            "success": False,
        }

        try:
            url = f"{self.backend_url}/api/generate"
            payload = {
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "num_predict": max_tokens,
                    "temperature": temperature,
                },
            }

            response = requests.post(url, json=payload, timeout=120)
            elapsed = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                response_text = data.get("response", "")

                # Calculate metrics
                # eval_count is the number of tokens generated
                eval_count = data.get("eval_count", 0)
                tokens_per_sec = (
                    round(eval_count / elapsed, 2) if elapsed > 0 else 0
                )

                metrics = MetricsData(
                    response_time_s=round(elapsed, 2),
                    tokens_per_sec=tokens_per_sec if eval_count > 0 else None,
                    ram_used_mb=round(self._get_memory_usage(), 1),
                    cpu_percent=self._get_cpu_percent(),
                )

                result["response"] = response_text
                result["metrics"] = metrics
                result["success"] = True
                self._last_metrics = metrics

                logger.debug(
                    f"Query completed in {elapsed:.2f}s, "
                    f"{eval_count} tokens, {tokens_per_sec} tok/s"
                )
            else:
                logger.error(f"Query failed: {response.status_code}")

        except requests.exceptions.Timeout:
            logger.error(f"Query timeout for model {self.model_name}")
        except Exception as e:
            logger.error(f"Query error: {e}")

        return result

    def get_metrics(self) -> Optional[MetricsData]:
        """Get last collected metrics."""
        return self._last_metrics

    def _get_memory_usage(self) -> float:
        """Get current memory usage in MB."""
        try:
            return self._process.memory_info().rss / (1024 * 1024)
        except Exception:
            return 0.0

    def _get_cpu_percent(self) -> Optional[float]:
        """Get CPU usage percent."""
        try:
            # Sample CPU usage over 0.1 second
            return self._process.cpu_percent(interval=0.1)
        except Exception:
            return None
