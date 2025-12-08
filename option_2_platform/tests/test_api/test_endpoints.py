import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch
from src.api.main import app
from src.api.dependencies import get_ingestion_pipeline, get_llm_chain, get_config
from src.rag.config import RAGConfig

client = TestClient(app)

# Mocks
mock_pipeline = MagicMock()
mock_llm_chain = MagicMock()
mock_config = RAGConfig()

def override_get_ingestion_pipeline():
    return mock_pipeline

def override_get_llm_chain():
    return mock_llm_chain

def override_get_config():
    return mock_config

app.dependency_overrides[get_ingestion_pipeline] = override_get_ingestion_pipeline
app.dependency_overrides[get_llm_chain] = override_get_llm_chain
app.dependency_overrides[get_config] = override_get_config

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "running"

def test_health_check():
    # Setup mock
    mock_llm_chain.llm_provider.is_available.return_value = True
    mock_llm_chain.llm_provider.base_url = "http://localhost:11434"
    mock_llm_chain.llm_provider.get_model_info.return_value = {
        "loaded": True,
        "name": "llama3",
        "size": "4.7GB"
    }
    mock_llm_chain.retrieval_engine.vector_store.collection.count.return_value = 10
    
    response = client.get("/system/health")
    assert response.status_code == 200
    data = response.json()
    assert data["ollama_available"] is True
    assert data["documents_count"] == 10

def test_upload_document():
    # Setup mock
    mock_pipeline.ingest_file.return_value = ["chunk1", "chunk2"]
    
    # Create dummy file
    file_content = b"dummy content"
    files = {"file": ("test.pdf", file_content, "application/pdf")}
    
    response = client.post("/ingest/upload", files=files)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["chunks_count"] == 2

def test_query_endpoint():
    # Setup mock
    mock_llm_chain.query.return_value = {
        "answer": "Test Answer",
        "sources": [{"source": "test.pdf", "page": 1, "chunk_id": 1, "score": 0.9}],
        "metadata": {}
    }
    
    payload = {"question": "Test Question"}
    response = client.post("/query", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["answer"] == "Test Answer"
    assert len(data["sources"]) == 1

def test_query_empty_question():
    payload = {"question": "   "}
    response = client.post("/query", json=payload)
    assert response.status_code == 400
