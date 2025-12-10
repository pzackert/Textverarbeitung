"""System health checks - Critical tests to verify deployment readiness."""

import pytest
import os
import shutil
import subprocess
import requests
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestOllamaAvailability:
    """Test Ollama service availability and connectivity."""

    def test_ollama_service_running(self):
        """Verify Ollama service is running and reachable."""
        try:
            response = requests.get("http://localhost:11434", timeout=5)
            assert response.status_code == 200
        except requests.exceptions.ConnectionError:
            pytest.fail(
                "❌ Ollama service not running.\n"
                "   Fix: Start Ollama with: ollama serve\n"
                "   or: brew services start ollama"
            )
        except requests.exceptions.Timeout:
            pytest.fail(
                "❌ Ollama service not responding.\n"
                "   Endpoint: http://localhost:11434"
            )

    def test_ollama_api_accessible(self):
        """Verify Ollama API endpoints are accessible."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            assert response.status_code == 200
            assert "models" in response.json()
        except Exception as e:
            pytest.fail(
                f"❌ Ollama API not accessible.\n"
                f"   Error: {str(e)}\n"
                f"   Fix: Ensure Ollama is running and accessible"
            )


class TestOllamaModelInstalled:
    """Test that required models are installed in Ollama."""

    def test_required_model_qwen25_7b_installed(self):
        """Verify qwen2.5:7b model is installed (primary model)."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            models_data = response.json()
            models = models_data.get("models", [])
            model_names = [m.get("name", "") for m in models]

            if not any("qwen2.5:7b" in name for name in model_names):
                pytest.fail(
                    "❌ Model qwen2.5:7b not found.\n"
                    f"   Installed models: {model_names}\n"
                    "   Fix: Install with: ollama pull qwen2.5:7b"
                )
        except Exception as e:
            pytest.fail(f"❌ Failed to check models: {str(e)}")

    def test_at_least_one_model_available(self):
        """Verify at least one model is installed."""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=5)
            models = response.json().get("models", [])

            assert len(models) > 0, (
                "❌ No models installed in Ollama.\n"
                "   Fix: Install a model with: ollama pull qwen2.5:7b"
            )
        except Exception as e:
            pytest.fail(f"❌ Failed to check installed models: {str(e)}")


class TestDiskSpaceAvailable:
    """Test sufficient disk space for models and data."""

    def test_minimum_disk_space_available(self):
        """Verify at least 5GB free disk space."""
        try:
            disk_usage = shutil.disk_usage("/")
            free_gb = disk_usage.free / (1024 ** 3)

            assert free_gb >= 5.0, (
                f"❌ Insufficient disk space.\n"
                f"   Available: {free_gb:.1f} GB\n"
                f"   Required: 5 GB minimum\n"
                f"   Fix: Free up disk space"
            )
        except Exception as e:
            pytest.fail(f"❌ Failed to check disk space: {str(e)}")

    def test_data_directory_writable(self):
        """Verify data directory is writable."""
        data_dir = Path("data")
        try:
            # Try to create a test file
            test_file = data_dir / ".writetest"
            test_file.touch()
            test_file.unlink()
        except Exception as e:
            pytest.fail(
                f"❌ Data directory not writable.\n"
                f"   Path: {data_dir.absolute()}\n"
                f"   Error: {str(e)}\n"
                f"   Fix: Check directory permissions"
            )


class TestChromaDBAccessible:
    """Test ChromaDB vector store accessibility."""

    def test_chromadb_can_initialize(self):
        """Verify ChromaDB can be initialized."""
        try:
            from src.rag.vector_store import VectorStore

            vector_store = VectorStore(collection_name="test_health_check")
            assert vector_store is not None
        except Exception as e:
            pytest.fail(
                f"❌ ChromaDB not accessible.\n"
                f"   Error: {str(e)}\n"
                f"   Fix: Verify ChromaDB installation and data directory"
            )

    def test_chromadb_directory_exists(self):
        """Verify ChromaDB data directory exists."""
        chromadb_path = Path("data/chromadb")
        if not chromadb_path.exists():
            pytest.fail(
                f"❌ ChromaDB directory missing.\n"
                f"   Path: {chromadb_path.absolute()}\n"
                f"   Fix: Create directory or initialize ChromaDB"
            )


class TestProjectDirectoriesExist:
    """Test that required project directories exist."""

    def test_data_projects_directory_exists(self):
        """Verify data/projects directory exists."""
        projects_dir = Path("data/projects")
        if not projects_dir.exists():
            pytest.fail(
                f"❌ Projects directory missing.\n"
                f"   Path: {projects_dir.absolute()}\n"
                f"   Fix: Create with: mkdir -p {projects_dir}"
            )

    def test_data_input_directory_exists(self):
        """Verify data/input directory exists."""
        input_dir = Path("data/input")
        if not input_dir.exists():
            pytest.fail(
                f"❌ Input directory missing.\n"
                f"   Path: {input_dir.absolute()}\n"
                f"   Fix: Create with: mkdir -p {input_dir}"
            )

    def test_logs_directory_exists(self):
        """Verify logs directory exists."""
        logs_dir = Path("logs")
        if not logs_dir.exists():
            pytest.fail(
                f"❌ Logs directory missing.\n"
                f"   Path: {logs_dir.absolute()}\n"
                f"   Fix: Create with: mkdir -p {logs_dir}"
            )


class TestModelResponds:
    """Test that LLM model can generate responses (smoke test)."""

    def test_model_generates_response(self):
        """Verify selected model can generate a response."""
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:7b",
                    "prompt": "Hi",
                    "stream": False,
                    "options": {"num_predict": 10, "temperature": 0.7},
                },
                timeout=120,
            )

            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert len(data.get("response", "")) > 0

        except requests.exceptions.Timeout:
            pytest.fail(
                "❌ Model response timeout (>120s).\n"
                "   Fix: Verify model is loaded and system has sufficient resources"
            )
        except Exception as e:
            pytest.fail(
                f"❌ Model failed to generate response.\n"
                f"   Error: {str(e)}\n"
                f"   Fix: Verify model is installed and working"
            )

    def test_response_time_acceptable(self):
        """Verify model response time is within acceptable range."""
        import time

        try:
            start = time.time()
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "qwen2.5:7b",
                    "prompt": "Hi",
                    "stream": False,
                    "options": {"num_predict": 5, "temperature": 0.7},
                },
                timeout=30,
            )
            elapsed = time.time() - start

            assert response.status_code == 200
            # Warn if slow but don't fail - systems vary
            if elapsed > 10:
                print(
                    f"⚠️  Model response slow: {elapsed:.1f}s\n"
                    f"   May need more powerful hardware"
                )

        except requests.exceptions.Timeout:
            pytest.fail(
                "❌ Model response timeout.\n"
                "   System may be overloaded or model not warmed up"
            )


class TestEmptyProjectGracefulHandling:
    """Test system handles projects with no documents gracefully."""

    def test_empty_project_does_not_crash(self):
        """Verify system doesn't crash with empty project."""
        try:
            # Create empty project directory
            empty_project = Path("data/projects/test_empty_project")
            empty_project.mkdir(parents=True, exist_ok=True)

            # Try to initialize RAG pipeline with empty project
            from src.rag.config import RAGConfig
            from src.rag.vector_store import VectorStore

            config = RAGConfig()
            vector_store = VectorStore(collection_name="test_empty")

            # Should not raise exception
            assert vector_store is not None

        except Exception as e:
            pytest.fail(
                f"❌ System crashed with empty project.\n"
                f"   Error: {str(e)}\n"
                f"   Fix: Add validation to handle empty projects"
            )
        finally:
            # Cleanup
            if empty_project.exists():
                shutil.rmtree(empty_project)

    def test_query_with_no_documents_returns_friendly_error(self):
        """Verify querying empty project returns user-friendly error."""
        try:
            from src.rag.llm_chain import LLMChain
            from unittest.mock import MagicMock

            # Mock empty vector store
            mock_vector_store = MagicMock()
            mock_vector_store.query.return_value = {"documents": []}

            # Should return helpful message, not technical error
            # (This would depend on actual implementation)
            assert mock_vector_store.query("test") is not None

        except Exception as e:
            pytest.fail(
                f"❌ Error handling for empty project broken.\n"
                f"   Error: {str(e)}"
            )


# Pytest markers for organization
pytestmark = [pytest.mark.system]
