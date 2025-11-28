"""Ollama Client - Direct GGUF Loading"""
import ollama
from typing import List, Optional
from backend.core.config import get_config_value
import logging

# Setup simple logger if not available
logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for Ollama using direct model loading"""
    
    def __init__(self):
        self.base_url = get_config_value('llm.base_url', 'http://localhost:11434')
        self.model = get_config_value('llm.model', 'qwen2.5:7b')
        self.temperature = get_config_value('llm.temperature', 0.1)
        self.max_tokens = get_config_value('llm.max_tokens', 2048)
        
        # Configure ollama client if needed (usually env vars or default)
        # ollama python client uses OLLAMA_HOST env var or defaults to localhost:11434
        
        logger.info(f"✓ OllamaClient initialized (Model: {self.model})")
    
    def generate(self, prompt: str, system_prompt: str = "", temperature: float = 0.0, max_tokens: int = 0) -> str:
        """Generate response from LLM"""
        
        temp = temperature if temperature > 0 else self.temperature
        # Note: ollama.generate doesn't strictly enforce max_tokens in the same way as OpenAI, 
        # but we can pass it in options.
        
        options = {
            "temperature": temp,
            "num_predict": max_tokens if max_tokens > 0 else self.max_tokens
        }

        try:
            response = ollama.generate(
                model=self.model,
                prompt=prompt,
                system=system_prompt,
                options=options
            )
            
            answer = response['response']
            logger.info(f"✓ LLM Response: {len(answer)} chars")
            return answer
        except Exception as e:
            logger.error(f"✗ LLM Error: {e}")
            return f"Error: {e}"
    
    def generate_with_context(self, query: str, context_chunks: List[str], system_prompt: str = "") -> str:
        """Generate response with RAG context"""
        context = "\n\n".join([f"[{i+1}] {chunk}" for i, chunk in enumerate(context_chunks)])
        prompt = f"""Context from documents:
{context}

Question: {query}

Answer based on the given context. If the information is not in the context, say so clearly."""
        return self.generate(prompt, system_prompt)
