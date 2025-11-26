import pytest
from fastapi.testclient import TestClient
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import sys

# Add project root to sys.path so we can import frontend.main
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

def test_app_initialization():
    """Test that the FastAPI app initializes correctly."""
    try:
        from frontend.main import app
    except ImportError:
        pytest.fail("Could not import 'app' from 'frontend.main'")

    client = TestClient(app)
    
    # Check if static files are mounted
    found_static = False
    for route in app.routes:
        if getattr(route, "path", "") == "/static" and isinstance(route.app, StaticFiles):
            found_static = True
            break
    assert found_static, "StaticFiles not mounted at '/static'"

def test_templates_setup():
    """Test that Jinja2Templates are configured correctly."""
    try:
        from frontend.main import templates
    except ImportError:
        pytest.fail("Could not import 'templates' from 'frontend.main'")
    
    assert isinstance(templates, Jinja2Templates)
    # Check if the directory exists
    assert os.path.isdir("frontend/templates"), "Templates directory does not exist"

def test_base_template_exists():
    """Test that base.html exists."""
    assert os.path.exists("frontend/templates/base.html"), "base.html does not exist"
