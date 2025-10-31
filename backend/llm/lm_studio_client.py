"""
LM Studio Client
Wrapper für LM Studio API (OpenAI-kompatibel)
"""

import requests
from typing import Optional, List, Dict, Any


class LMStudioClient:
    """Wrapper für LM Studio API (OpenAI-kompatibel)."""
    
    def __init__(
        self,
        base_url: str = "http://localhost:1234/v1",
        api_key: str = "not-needed"
    ):
        self.base_url = base_url
        self.api_key = api_key
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
        **kwargs
    ) -> str:
        """
        Generiert Text mit LM Studio.
        
        Args:
            prompt: User-Prompt
            system_prompt: System-Prompt (optional)
            temperature: Sampling-Temperatur (0.0 - 1.0)
            max_tokens: Maximale Token-Anzahl
            
        Returns:
            Generierter Text
        """
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": "local-model",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens,
                **kwargs
            },
            headers={"Authorization": f"Bearer {self.api_key}"}
        )
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
    
    def is_available(self) -> bool:
        """Prüft ob LM Studio Server erreichbar ist."""
        try:
            response = requests.get(f"{self.base_url}/models", timeout=2)
            return response.status_code == 200
        except Exception:
            return False
