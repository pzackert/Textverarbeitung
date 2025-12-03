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

class OllamaProvider(BaseLLMProvider):
    """Ollama LLM provider implementation."""
    
    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        """Generate response from LLM."""
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
        try:
            # Simple check to root endpoint
            response = requests.get(self.base_url, timeout=5)
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

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
            url = f"{self.base_url}/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            models_data = response.json()
            models = models_data.get("models", [])
            
            # models is a list of dicts, e.g. [{'name': 'qwen2.5:7b', ...}]
            model_names = [m.get("name") for m in models]
            
            # Check for exact match or match with :latest
            # Also handle cases where user config has 'qwen2.5:7b' but ollama has 'qwen2.5:7b'
            if self.model_name in model_names:
                status["available"] = True
                status["model_info"] = f"Model {self.model_name} found."
            elif f"{self.model_name}:latest" in model_names:
                # If user asked for 'model' but 'model:latest' exists, that's usually fine in Ollama logic,
                # but strictly speaking we want to know if the requested model is there.
                # Ollama usually normalizes names.
                status["available"] = True
                status["model_info"] = f"Model {self.model_name}:latest found."
            else:
                status["error"] = f"Model {self.model_name} not found in Ollama. Available: {', '.join(model_names)}"
                
        except requests.exceptions.RequestException as e:
            status["error"] = f"Failed to fetch models from Ollama: {e}"
            
        return status
