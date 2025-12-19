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
    tokens_generated: Optional[int] = None
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
        # Allow overriding the backend URL (LM Studio uses 1234 by default)
        env_base = os.getenv("LLM_BASE_URL")
        self.backend_url = (env_base or backend_url).rstrip("/")
        self._process = psutil.Process(os.getpid())
        self._last_metrics: Optional[MetricsData] = None
        self._supports_openai = False

    def check_availability(self) -> bool:
        """Check if Ollama service and model are available."""
        try:
            # Try OpenAI-compatible listing first (LM Studio)
            resp = requests.get(f"{self.backend_url}/v1/models", timeout=5)
            if resp.status_code == 200 and isinstance(resp.json(), dict):
                data = resp.json().get("data", []) or []
                names = [m.get("id", "") for m in data]
                if any(self.model_name == n or self.model_name in n for n in names):
                    self._supports_openai = True
                    logger.info(f"Model {self.model_name} available via /v1/models")
                    return True

            # Fallback to Ollama tags if OpenAI-style not available
            ping = requests.get(self.backend_url, timeout=5)
            if ping.status_code != 200:
                logger.warning(f"Service returned status {ping.status_code}")
                return False

            tags = requests.get(f"{self.backend_url}/api/tags", timeout=5)
            if tags.status_code != 200:
                logger.warning("Failed to fetch model tags")
                return False

            models = tags.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            if any(self.model_name == n or self.model_name in n for n in model_names):
                logger.info(f"Model {self.model_name} available via /api/tags")
                return True

            logger.warning(f"Model {self.model_name} not found. Available: {model_names}")
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
            # Prefer OpenAI-style warmup for LM Studio
            url_chat = f"{self.backend_url}/v1/chat/completions"
            chat_payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": "Hi"}],
                "max_tokens": 1,
                "stream": False,
            }

            response = requests.post(url_chat, json=chat_payload, timeout=120)
            if response.status_code == 404:
                # Fallback to Ollama generate
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
                metrics["warmup_time_s"] = max(round(elapsed, 2), 0.01)
                metrics["success"] = True
                metrics["ram_used_mb"] = round(self._get_memory_usage(), 1)
                logger.info(
                    f"Model {self.model_name} warmed up in {metrics['warmup_time_s']:.2f}s"
                )
            else:
                logger.error(f"Failed to load model: {response.status_code}")

        except requests.exceptions.Timeout:
            logger.error(f"Timeout loading model {self.model_name}")
            elapsed = time.time() - start_time
            metrics["warmup_time_s"] = max(round(elapsed, 2), 0.01)
        except Exception as e:
            logger.error(f"Error loading model: {e}")

        return metrics

    def query(
        self,
        prompt: str,
        temperature: float = 0.7,
        max_tokens: int = 1024,
        context_length: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Query the LLM and collect metrics.

        Args:
            prompt: Prompt to send to the model
            temperature: Temperature parameter
            max_tokens: Maximum tokens to generate
            context_length: Optional context window length (passes num_ctx to Ollama)

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
            if self._supports_openai:
                url = f"{self.backend_url}/v1/chat/completions"
                payload = {
                    "model": self.model_name,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": False,
                }
                response = requests.post(url, json=payload, timeout=120)
            else:
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

                if context_length:
                    payload["options"]["num_ctx"] = context_length

                response = requests.post(url, json=payload, timeout=120)
            elapsed = time.time() - start_time

            if response.status_code == 200:
                data = response.json()
                response_text = ""
                if self._supports_openai:
                    choices = data.get("choices", []) or []
                    if choices and "message" in choices[0]:
                        response_text = choices[0]["message"].get("content", "")
                else:
                    response_text = data.get("response", "")

                # Drop empty generations early so callers can skip on failure
                if not response_text.strip():
                    logger.error("Query returned empty response text")
                    return result

                # Calculate metrics
                # eval_count is the number of tokens generated
                eval_count = data.get("eval_count", 0)
                tokens_per_sec = (
                    round(eval_count / elapsed, 2) if elapsed > 0 else 0
                )

                metrics = MetricsData(
                    response_time_s=round(elapsed, 2),
                    tokens_per_sec=tokens_per_sec if eval_count > 0 else None,
                    tokens_generated=eval_count if eval_count > 0 else None,
                    ram_used_mb=round(self._get_memory_usage(), 1),
                    cpu_percent=self._get_cpu_percent(),
                )

                result["response"] = response_text
                result["metrics"] = metrics
                result["success"] = True
                result["tokens_generated"] = eval_count
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
