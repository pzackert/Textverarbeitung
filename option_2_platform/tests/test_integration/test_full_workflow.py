import pytest
import os
import time
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.main import app
from src.api.dependencies import get_ingestion_pipeline, get_llm_chain, get_config
from src.rag.config import RAGConfig

# We use TestClient for integration testing the unified app
client = TestClient(app)

# Mocks for RAG components to avoid needing actual Ollama/ChromaDB running during CI/Test
mock_pipeline = MagicMock()
mock_llm_chain = MagicMock()
mock_config = RAGConfig()

def override_get_ingestion_pipeline():
    return mock_pipeline

def override_get_llm_chain():
    return mock_llm_chain

def override_get_config():
    return mock_config

# Apply overrides
app.dependency_overrides[get_ingestion_pipeline] = override_get_ingestion_pipeline
app.dependency_overrides[get_llm_chain] = override_get_llm_chain
app.dependency_overrides[get_config] = override_get_config

class TestFullWorkflow:
    
    def setup_method(self):
        # Reset mocks
        mock_pipeline.reset_mock()
        mock_llm_chain.reset_mock()
        
        # Setup default behaviors
        mock_llm_chain.llm_provider.is_available.return_value = True
        mock_llm_chain.retrieval_engine.vector_store.collection.count.return_value = 5
        
        mock_pipeline.ingest_file.return_value = ["chunk1", "chunk2", "chunk3"]
        
        mock_llm_chain.query.return_value = {
            "answer": "This is a test answer based on the document.",
            "sources": [
                {"source": "test_doc.pdf", "page": 1, "chunk_id": 1, "score": 0.95},
                {"source": "test_doc.pdf", "page": 2, "chunk_id": 2, "score": 0.85}
            ],
            "metadata": {"retrieval_time": 0.1, "llm_time": 1.5}
        }

    def test_dashboard_load(self):
        """Test that the dashboard loads and shows status."""
        # Mock api_client.get_system_stats to avoid actual HTTP call
        with patch("frontend.routers.dashboard.api_client.get_system_stats") as mock_stats:
            mock_stats.return_value = {"documents_count": 5}
            
            response = client.get("/")
            assert response.status_code == 200
            assert "IFB" in response.text
            assert "Dashboard" in response.text
            # Check if stats are rendered (mocked)
            assert "Running" in response.text  # Ollama status

    def test_chat_page_load(self):
        """Test that chat page loads."""
        response = client.get("/chat")
        assert response.status_code == 200
        assert "IFB Chat" in response.text
        assert "System Status" in response.text

    def test_document_upload_flow(self):
        """Test the full upload flow via Frontend -> API -> RAG."""
        # 1. Create a dummy project first (if needed by logic, but here we mock)
        # In our implementation, upload saves to project then calls API
        
        # Mock project service save_document to return a path
        with patch("frontend.routers.projects.project_service.save_document") as mock_save:
            mock_save.return_value = "data/projects/test-project/documents/test.pdf"
            
            # Mock API client upload_document to avoid actual HTTP call in unit test context
            # But wait, TestClient calls the app directly. 
            # The frontend router calls `api_client.upload_document`.
            # `api_client` uses `httpx`. We need to mock `api_client` or `httpx`.
            
            with patch("frontend.routers.projects.api_client.upload_document") as mock_api_upload:
                mock_api_upload.return_value = {"success": True, "chunks_count": 3}
                
                file_content = b"dummy pdf content"
                files = {"file": ("test.pdf", file_content, "application/pdf")}
                
                response = client.post("/projects/test-project/upload", files=files)
                
                assert response.status_code == 200
                assert "Success!" in response.text
                assert "3 chunks created" in response.text
                
                # Verify API client was called
                mock_api_upload.assert_called_once()

    def test_chat_query_flow(self):
        """Test the chat query flow via Frontend -> API -> RAG."""
        
        with patch("frontend.routers.chat.api_client.query_rag") as mock_api_query:
            mock_api_query.return_value = {
                "answer": "This is a test answer.",
                "sources": [{"source_file": "test.pdf", "page_number": 1}],
                "citations": [{"citation_number": 1, "source": {"source_file": "test.pdf"}}]
            }
            
            response = client.post("/chat/query", data={"question": "What is the funding?"})
            
            assert response.status_code == 200
            assert "This is a test answer." in response.text
            assert "test.pdf" in response.text
            
            mock_api_query.assert_called_once_with("What is the funding?")

if __name__ == "__main__":
    # Manual run setup if executed directly
    pass
