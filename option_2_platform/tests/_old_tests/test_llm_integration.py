import pytest
from backend.llm.ollama_client import OllamaClient

@pytest.mark.integration
def test_ollama_real_connection():
    """
    Real integration test with Ollama.
    Requires Ollama running and qwen2.5:0.5b pulled.
    """
    client = OllamaClient()
    
    # Simple prompt
    response = client.generate("Say 'Hello World'", max_tokens=10)
    
    print(f"LLM Response: {response}")
    assert response is not None
    assert len(response) > 0
    # Check for error message
    assert "Error:" not in response
    assert "Fehler:" not in response

if __name__ == "__main__":
    test_ollama_real_connection()
