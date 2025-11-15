"""LM Studio Client - OpenAI-kompatible API"""
from typing import List
from openai import OpenAI
from backend.utils.config import get_config_value
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class LMStudioClient:
    """Client für LM Studio mit OpenAI API"""
    
    def __init__(self):
        base_url = get_config_value('llm.base_url')
        self.client = OpenAI(base_url=base_url, api_key="not-needed")
        self.model = get_config_value('llm.model', 'qwen2.5-4b-instruct')
        self.temperature = get_config_value('llm.temperature', 0.1)
        self.max_tokens = get_config_value('llm.max_tokens', 1024)
        logger.info(f"✓ LMStudioClient initialisiert ({base_url})")
    
    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.0, max_tokens: int = 0) -> str:
        """Generiere Antwort vom LLM"""
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        temp = temperature if temperature > 0 else self.temperature
        tokens = max_tokens if max_tokens > 0 else self.max_tokens
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=temp,
                max_tokens=tokens
            )
            answer = response.choices[0].message.content or ""
            logger.info(f"✓ LLM Antwort: {len(answer)} Zeichen")
            return answer
        except Exception as e:
            logger.error(f"✗ LLM Fehler: {e}")
            return f"Fehler: {e}"
    
    def generate_with_context(self, query: str, context_chunks: List[str], system_prompt: str = "") -> str:
        """Generiere Antwort mit RAG-Kontext"""
        context = "\n\n".join([f"[{i+1}] {chunk}" for i, chunk in enumerate(context_chunks)])
        prompt = f"""Kontext aus den Förderrichtlinien:
{context}

Frage: {query}

Antworte basierend auf dem gegebenen Kontext. Wenn die Information nicht im Kontext vorhanden ist, sage das klar."""
        return self.generate(prompt, system_prompt)

