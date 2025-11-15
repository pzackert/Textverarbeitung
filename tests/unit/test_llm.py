"""Test: LLM Integration (LM Studio Client)"""
import pytest
from backend.llm.lm_studio_client import LMStudioClient


@pytest.mark.integration
def test_llm_connection():
    """Test LM Studio Connection"""
    client = LMStudioClient()
    
    # Simple prompt
    response = client.generate("Was ist 2+2? Antworte nur mit der Zahl.")
    
    assert response is not None
    assert len(response) > 0
    assert not response.startswith("Fehler")


@pytest.mark.integration
def test_llm_with_context():
    """Test LLM mit RAG-Kontext"""
    client = LMStudioClient()
    
    context = [
        "Das Unternehmen hat seinen Sitz in Erfurt, Thüringen.",
        "Die Fördersumme beträgt 150.000 Euro."
    ]
    
    query = "Wo ist das Unternehmen ansässig?"
    response = client.generate_with_context(query, context)
    
    assert response is not None
    assert len(response) > 0
    # Should mention Thüringen or Erfurt
    assert "Thüringen" in response or "Erfurt" in response or "thüringen" in response.lower()
