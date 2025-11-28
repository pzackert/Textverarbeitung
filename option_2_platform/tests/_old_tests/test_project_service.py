import pytest
import shutil
from pathlib import Path
from datetime import datetime
from backend.core.models import Project, Document
from backend.services.project_service import ProjectService

# Test Data Directory
TEST_DATA_DIR = Path("temp/data/projects")

@pytest.fixture
def project_service():
    # Setup
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)
    TEST_DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    service = ProjectService(storage_root=TEST_DATA_DIR)
    yield service
    
    # Teardown
    if TEST_DATA_DIR.exists():
        shutil.rmtree(TEST_DATA_DIR)

def test_project_model():
    """Test Project model validation."""
    p = Project(id="123", name="Test Project", description="Desc")
    assert p.id == "123"
    assert p.name == "Test Project"
    assert isinstance(p.created_at, datetime)

def test_create_project(project_service):
    """Test creating a project."""
    project = project_service.create_project(name="My Project", description="My Description")
    
    assert project.name == "My Project"
    assert project.description == "My Description"
    assert (TEST_DATA_DIR / project.id).exists()
    assert (TEST_DATA_DIR / project.id / "metadata.json").exists()

def test_list_projects(project_service):
    """Test listing projects."""
    project_service.create_project(name="P1")
    project_service.create_project(name="P2")
    
    projects = project_service.list_projects()
    assert len(projects) == 2
    names = [p.name for p in projects]
    assert "P1" in names
    assert "P2" in names

def test_get_project(project_service):
    """Test getting a single project."""
    created = project_service.create_project(name="Target")
    fetched = project_service.get_project(created.id)
    
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.name == "Target"

def test_get_nonexistent_project(project_service):
    """Test getting a project that doesn't exist."""
    assert project_service.get_project("fake-id") is None
