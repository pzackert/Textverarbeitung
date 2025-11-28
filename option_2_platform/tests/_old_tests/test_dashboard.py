import pytest
from fastapi.testclient import TestClient
from frontend.main import app
from backend.services.project_service import ProjectService
from backend.dependencies import get_project_service
from backend.core.models import Project
import shutil
from pathlib import Path

# Mock Data Directory
TEST_DATA_DIR = Path("temp/data/projects_ui_test")

# Create a single instance for the test session to persist state
_test_service_instance = None

def get_test_project_service():
    global _test_service_instance
    if _test_service_instance is None:
        if TEST_DATA_DIR.exists():
            shutil.rmtree(TEST_DATA_DIR)
        TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
        _test_service_instance = ProjectService(storage_root=TEST_DATA_DIR)
    return _test_service_instance

# Override dependency
app.dependency_overrides[get_project_service] = get_test_project_service

client = TestClient(app)

def test_dashboard_route():
    """Test that the dashboard loads."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Textverarbeitung" in response.text

def test_create_project_ui():
    """Test creating a project via the UI form."""
    response = client.post("/projects", data={"name": "UI Project", "description": "Created via UI"})
    
    # Should redirect or return HTMX content. For MVP, let's assume redirect to dashboard or project list.
    # Adjust expectation based on implementation.
    assert response.status_code in [200, 302, 303]
    
    # Verify project was created
    service = get_test_project_service()
    projects = service.list_projects()
    assert any(p.name == "UI Project" for p in projects)

def teardown_module():
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)
