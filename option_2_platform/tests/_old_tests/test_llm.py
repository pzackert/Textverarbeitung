import pytest
from unittest.mock import patch, MagicMock
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.llm.ollama_client import OllamaClient

def test_ollama_client_initialization():
    client = OllamaClient()
    # Check if defaults are loaded from config or fallback
    assert client.model is not None

@patch('backend.llm.ollama_client.ollama.generate')
def test_ollama_generate(mock_generate):
    mock_generate.return_value = {'response': 'Hello there!'}
    
    client = OllamaClient()
    response = client.generate("Hello")
    
    assert response == "Hello there!"
    mock_generate.assert_called_once()
    args, kwargs = mock_generate.call_args
    assert kwargs['model'] == client.model
    assert kwargs['prompt'] == "Hello"
