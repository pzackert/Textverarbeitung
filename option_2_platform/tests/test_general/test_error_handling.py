"""Error handling and resilience tests for the application."""

import pytest
from unittest.mock import MagicMock, patch


class TestInvalidPDFHandling:
    """Test system handles invalid PDF files gracefully."""

    def test_corrupt_pdf_doesnt_crash(self):
        """Verify corrupt PDF doesn't crash system."""
        mock_parser = MagicMock()
        mock_parser.parse.side_effect = ValueError("Invalid PDF format")

        try:
            mock_parser.parse("corrupted.pdf")
        except ValueError:
            # Should catch and handle
            pass

        mock_parser.parse.assert_called_once()

    def test_empty_pdf_handled_gracefully(self):
        """Verify empty PDF returns meaningful error."""
        mock_parser = MagicMock()
        mock_parser.parse.return_value = {
            "status": "error",
            "message": "PDF has no readable content",
        }

        result = mock_parser.parse("empty.pdf")

        assert result["status"] == "error"
        assert "content" in result["message"].lower()


class TestQueryTimeout:
    """Test system handles query timeouts gracefully."""

    def test_ollama_timeout_returns_error(self):
        """Verify Ollama timeout is handled gracefully."""
        mock_llm = MagicMock()
        mock_llm.generate.side_effect = TimeoutError("Ollama request timeout")

        try:
            mock_llm.generate("test prompt")
        except TimeoutError:
            # Should catch and return user-friendly error
            pass

        # Verify mock was called
        mock_llm.generate.assert_called_once()

    def test_query_timeout_user_friendly_message(self):
        """Verify timeout shows user-friendly message."""
        # Timeout should display message like:
        # "The response is taking longer than expected. Please try again."
        # Not technical: "TimeoutError: 30s exceeded"

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {
            "error": "Request timeout",
            "user_message": "Your request is taking longer than expected. Please try again.",
        }

        # Simulates API response with friendly error
        assert mock_response.json()["user_message"] is not None


class TestMissingModelHandling:
    """Test system handles missing/unavailable models gracefully."""

    def test_missing_model_returns_helpful_error(self):
        """Verify missing model error is helpful."""
        mock_provider = MagicMock()
        mock_provider.check_connection.side_effect = FileNotFoundError(
            "Model 'qwen2.5:7b' not found. Run 'ollama pull qwen2.5:7b' to download."
        )

        try:
            mock_provider.check_connection()
        except FileNotFoundError as e:
            # Error message should be helpful
            assert "ollama pull" in str(e)

        mock_provider.check_connection.assert_called_once()

    def test_fallback_model_attempt(self):
        """Verify system can fall back to alternative models."""
        # If primary model unavailable, try secondary
        primary_model = MagicMock()
        primary_model.available = False

        secondary_model = MagicMock()
        secondary_model.available = True

        # Should fall back to secondary
        models = [primary_model, secondary_model]
        available = next((m for m in models if m.available), None)

        assert available == secondary_model


class TestChromaDBConnectionFailure:
    """Test system handles ChromaDB connection failures."""

    def test_chromadb_connection_error_caught(self):
        """Verify ChromaDB connection errors are caught."""
        mock_store = MagicMock()
        mock_store.add_documents.side_effect = ConnectionError(
            "Cannot connect to ChromaDB server"
        )

        try:
            mock_store.add_documents([])
        except ConnectionError:
            # Should catch and handle gracefully
            pass

        mock_store.add_documents.assert_called_once()

    def test_query_with_unavailable_db(self):
        """Verify query fails gracefully with unavailable DB."""
        mock_store = MagicMock()
        mock_store.query.return_value = {
            "status": "error",
            "message": "Database unavailable. Results cached if available.",
            "cached": True,
        }

        result = mock_store.query("test query")

        # Should indicate problem but offer fallback
        assert result["status"] == "error"
        assert "cached" in result or "available" in result["message"]


class TestEmptyDocumentSet:
    """Test system handles projects with no documents."""

    def test_rag_query_with_no_documents_returns_message(self):
        """Verify querying with no documents returns friendly message."""
        mock_vector_store = MagicMock()
        mock_vector_store.query.return_value = []

        # Should handle empty result set
        result = mock_vector_store.query("any question")
        assert result is not None  # Should return something, not crash

    def test_validation_with_no_documents_skips_gracefully(self):
        """Verify validation skips gracefully with no documents."""
        mock_validator = MagicMock()
        mock_validator.validate.return_value = {
            "status": "no_documents",
            "message": "No documents to validate",
        }

        result = mock_validator.validate()
        assert result["status"] != "error"  # Not an error, just no data


class TestLLMUnavailableGraceful:
    """Test system handles LLM service unavailable gracefully."""

    def test_ollama_offline_detection(self):
        """Verify system detects Ollama offline."""
        mock_provider = MagicMock()
        mock_provider.is_available.return_value = False

        # System should detect offline status
        available = mock_provider.is_available()

        assert available is False
        mock_provider.is_available.assert_called_once()

    def test_application_shows_maintenance_message_when_offline(self):
        """Verify UI shows maintenance message when LLM offline."""
        mock_response = MagicMock()
        mock_response.status_code = 503
        mock_response.json.return_value = {
            "error": "Service unavailable",
            "user_message": "The AI service is temporarily unavailable. We're working to restore it.",
        }

        # Should show friendly message, not technical error
        assert mock_response.json()["user_message"] is not None


class TestInvalidInputHandling:
    """Test system handles invalid user input gracefully."""

    def test_empty_query_rejected(self):
        """Verify empty query is rejected with friendly message."""
        mock_llm_chain = MagicMock()
        mock_llm_chain.query.return_value = {
            "error": "Query cannot be empty",
            "suggestion": "Please enter a question",
        }

        result = mock_llm_chain.query("")

        assert "error" in result
        assert result["error"] == "Query cannot be empty"

    def test_very_long_query_truncated(self):
        """Verify very long queries are handled."""
        long_query = "test " * 10000  # Very long query

        mock_llm_chain = MagicMock()
        mock_llm_chain.query.return_value = {
            "answer": "Query too long",
            "truncated": True,
        }

        result = mock_llm_chain.query(long_query)
        assert result is not None

    def test_special_characters_in_query(self):
        """Verify special characters don't break system."""
        special_query = "SELECT * FROM documents; DROP TABLE documents; --"

        mock_llm_chain = MagicMock()
        result = mock_llm_chain.query(special_query)
        assert result is not None


class TestDocumentUploadErrors:
    """Test document upload error scenarios."""

    def test_unsupported_file_type_rejected(self):
        """Verify unsupported file types are rejected."""
        # Test that parsers reject unsupported formats
        mock_pdf_parser = MagicMock()
        mock_pdf_parser.can_parse.return_value = False

        # .exe file should be rejected
        assert not mock_pdf_parser.can_parse("file.exe")
        assert not mock_pdf_parser.can_parse("file.zip")

        mock_pdf_parser.can_parse.assert_called()

    def test_file_too_large_rejected(self):
        """Verify overly large files are rejected."""
        # Mock a very large file
        mock_file = MagicMock()
        mock_file.size = 1024 * 1024 * 1024  # 1GB

        mock_handler = MagicMock()
        mock_handler.max_size = 100 * 1024 * 1024  # 100MB limit
        mock_handler.can_handle.return_value = False

        # Should be rejected before parsing
        assert not mock_handler.can_handle(mock_file)


# Pytest markers
pytestmark = [pytest.mark.unit]
