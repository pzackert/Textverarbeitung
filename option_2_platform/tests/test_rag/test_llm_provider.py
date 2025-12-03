import pytest
from unittest.mock import Mock, patch
from src.rag.llm_provider import OllamaProvider
import requests

class TestOllamaProvider:
    
    @pytest.fixture
    def provider(self):
        return OllamaProvider(model_name="test-model", base_url="http://localhost:11434")

    def test_ollama_provider_initialization(self, provider):
        assert provider.model_name == "test-model"
        assert provider.base_url == "http://localhost:11434"

    @patch('requests.get')
    def test_connection_check_success(self, mock_get, provider):
        # Mock is_available check
        mock_response_root = Mock()
        mock_response_root.status_code = 200
        
        # Mock tags check
        mock_response_tags = Mock()
        mock_response_tags.status_code = 200
        mock_response_tags.json.return_value = {
            "models": [{"name": "test-model"}, {"name": "other-model"}]
        }
        
        mock_get.side_effect = [mock_response_root, mock_response_tags]
        
        status = provider.test_connection()
        assert status["available"] is True
        assert "test-model found" in status["model_info"]

    @patch('requests.get')
    def test_connection_check_failure_offline(self, mock_get, provider):
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")
        
        status = provider.test_connection()
        assert status["available"] is False
        assert "not reachable" in status["error"]

    @patch('requests.get')
    def test_connection_check_model_missing(self, mock_get, provider):
        # Mock is_available check
        mock_response_root = Mock()
        mock_response_root.status_code = 200
        
        # Mock tags check
        mock_response_tags = Mock()
        mock_response_tags.status_code = 200
        mock_response_tags.json.return_value = {
            "models": [{"name": "other-model"}]
        }
        
        mock_get.side_effect = [mock_response_root, mock_response_tags]
        
        status = provider.test_connection()
        assert status["available"] is False
        assert "not found" in status["error"]

    @patch('requests.post')
    def test_generate_response(self, mock_post, provider):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test response"}
        mock_post.return_value = mock_response
        
        response = provider.generate("Test prompt", 100, 0.7)
        assert response == "Test response"
        
        # Verify payload
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        assert kwargs['json']['model'] == "test-model"
        assert kwargs['json']['prompt'] == "Test prompt"
        assert kwargs['json']['options']['temperature'] == 0.7

    @patch('requests.post')
    def test_connection_timeout(self, mock_post, provider):
        mock_post.side_effect = requests.exceptions.Timeout("Timeout")
        
        with pytest.raises(ConnectionError) as excinfo:
            provider.generate("Test prompt", 100, 0.7)
        assert "Failed to connect" in str(excinfo.value)

    @patch('requests.post')
    def test_invalid_endpoint(self, mock_post, provider):
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_post.return_value = mock_response
        
        with pytest.raises(ConnectionError):
            provider.generate("Test prompt", 100, 0.7)
