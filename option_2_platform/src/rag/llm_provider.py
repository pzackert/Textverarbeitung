import logging
import requests
from abc import ABC, abstractmethod
from typing import Dict, Any

logger = logging.getLogger(__name__)

class BaseLLMProvider(ABC):
    """Base class for LLM providers (Ollama, LM Studio, vLLM)."""
    
    def __init__(self, model_name: str, base_url: str):
        """Initialize provider with model and endpoint."""
        self.model_name = model_name
        self.base_url = base_url.rstrip('/')
        
    @abstractmethod
    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate response from LLM."""
        pass
        
    @abstractmethod
    def is_available(self) -> bool:
        """Check if LLM service is running and accessible."""
        pass

    def get_model_info(self) -> Dict[str, Any]:
        """Get info about the configured model."""
        return {"loaded": False, "name": self.model_name, "size": None}

class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider implementation."""

    def __init__(self, model_name: str, base_url: str):
        super().__init__(model_name, base_url)
        # Flag toggled after availability check; enables OpenAI-compatible flow for LM Studio
        self._supports_openai = self._should_probe_openai()

    def _should_probe_openai(self) -> bool:
        """Heuristic to decide whether to check OpenAI-compatible endpoints."""
        return "1234" in self.base_url or "/v1" in self.base_url or "lmstudio" in self.base_url
    
    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate response from LLM."""
        # Prefer OpenAI-compatible route when supported (LM Studio), otherwise use Ollama API
        if self._supports_openai:
            url = f"{self.base_url}/v1/chat/completions"
            payload = {
                "model": self.model_name,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "stream": False,
            }
            logger.info(f"Sending request to OpenAI-compatible endpoint: {url}, model={self.model_name}")
            try:
                response = requests.post(url, json=payload, timeout=60)
                # LM Studio may return 404 if OpenAI route is disabled; fallback to Ollama flow
                if response.status_code != 404:
                    response.raise_for_status()
                    data = response.json()
                    choices = data.get("choices", [])
                    if choices and "message" in choices[0]:
                        return choices[0]["message"].get("content", "")
                    return data.get("response", "")
            except requests.exceptions.RequestException as e:
                logger.warning(f"OpenAI-compatible request failed, falling back to Ollama API: {e}")

        url = f"{self.base_url}/api/generate"
        payload = {
            "model": self.model_name,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature
            }
        }
        
        logger.info(f"Sending request to Ollama: {url}, model={self.model_name}")
        
        try:
            response = requests.post(url, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()
            return data.get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama request failed: {e}")
            raise ConnectionError(f"Failed to connect to Ollama: {e}")

    def is_available(self) -> bool:
        """Check if LLM service is running and accessible."""
        # Try OpenAI-compatible discovery first (LM Studio)
        if self._should_probe_openai():
            try:
                models_resp = requests.get(f"{self.base_url}/v1/models", timeout=5)
                if models_resp.status_code == 200:
                    body = models_resp.json()
                    if isinstance(body, dict):
                        data = body.get("data", []) or []
                        if isinstance(data, list):
                            names = [m.get("id", "") for m in data]
                            if any(self.model_name == n or self.model_name in n for n in names):
                                self._supports_openai = True
                                return True
            except requests.exceptions.RequestException:
                pass

        try:
            # Simple check to root endpoint
            response = requests.get(self.base_url, timeout=5)
            if response.status_code != 200:
                return False
        except requests.exceptions.RequestException:
            return False
        return True

    def get_model_info(self) -> Dict[str, Any]:
        """Get info about the configured model."""
        if self._supports_openai:
            try:
                url = f"{self.base_url}/v1/models"
                response = requests.get(url, timeout=5)
                if response.status_code == 200:
                    models = response.json().get("data", []) or []
                    for m in models:
                        if self.model_name == m.get("id") or self.model_name in m.get("id", ""):
                            return {
                                "loaded": True,
                                "name": m.get("id"),
                                "size": m.get("object"),
                            }
            except Exception as e:
                logger.error(f"Failed to get OpenAI-style model info: {e}")

        try:
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=5)
            if response.status_code != 200:
                return {"loaded": False, "name": self.model_name, "size": None}
                
            models_data = response.json()
            models = models_data.get("models", [])
            
            for m in models:
                if self.model_name in m.get("name", ""):
                    size_gb = m.get("size", 0) / (1024**3)
                    return {
                        "loaded": True,
                        "name": m.get("name"),
                        "size": f"{size_gb:.1f}GB"
                    }
            
            return {"loaded": False, "name": self.model_name, "size": None}
        except Exception as e:
            logger.error(f"Failed to get model info: {e}")
            return {"loaded": False, "name": self.model_name, "size": None}

    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Ollama.
        Returns status dict with availability and model info.
        """
        status = {
            "available": False,
            "model_info": None,
            "error": None
        }
        
        if not self.is_available():
            status["error"] = "Ollama service is not reachable. Please ensure Ollama is running (e.g., 'ollama serve')."
            return status
            
        # Check if model exists
        try:
            if self._supports_openai:
                url = f"{self.base_url}/v1/models"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                models = response.json().get("data", []) or []
                model_names = [m.get("id", "") for m in models]
            else:
                url = f"{self.base_url}/api/tags"
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                models_data = response.json()
                models = models_data.get("models", [])
                model_names = [m.get("name") for m in models]
            
            if self.model_name in model_names:
                status["available"] = True
                status["model_info"] = f"Model {self.model_name} found."
            elif f"{self.model_name}:latest" in model_names:
                status["available"] = True
                status["model_info"] = f"Model {self.model_name}:latest found."
            else:
                status["error"] = f"Model {self.model_name} not found in Ollama. Available: {', '.join(model_names)}"
                
        except requests.exceptions.RequestException as e:
            status["error"] = f"Failed to fetch models from Ollama: {e}"
            
        return status
