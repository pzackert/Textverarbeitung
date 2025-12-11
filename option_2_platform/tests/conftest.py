"""Pytest configuration and shared fixtures.

This module provides centralized pytest configuration and fixtures for the test suite.

CURRENT STATUS:
- No fixtures currently defined
- Minimal configuration
- Available for expansion as test suite grows

FIXTURE TEMPLATES (for future use):

@pytest.fixture
def test_client():
    '''FastAPI test client for API endpoint testing.'''
    from fastapi.testclient import TestClient
    # Import and return test client

@pytest.fixture
def mock_llm():
    '''Mocked LLM client for unit tests without hitting Ollama.'''
    # Return mock LLM client

@pytest.fixture
def temp_project(tmp_path):
    '''Temporary project directory for testing.'''
    project_dir = tmp_path / "test_project"
    project_dir.mkdir()
    return project_dir

USED BY:
- test_api/: (when API test client fixture is added)
- test_integration/: (when integration fixtures are added)

FUTURE IMPROVEMENTS:
- Add FastAPI test client fixture
- Add mock LLM fixtures
- Add temporary directory fixtures
- Add database fixtures (ChromaDB mocks)
- Add project/document fixtures
"""
import pytest

# Add shared fixtures here
