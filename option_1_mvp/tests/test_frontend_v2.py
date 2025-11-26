from fastapi.testclient import TestClient
from frontend_v2.main import app
from frontend_v2.mock_data import PROJECTS

client = TestClient(app)

def test_read_dashboard():
    response = client.get("/")
    assert response.status_code == 200
    assert "Dashboard" in response.text

def test_read_projects():
    response = client.get("/antraege")
    assert response.status_code == 200
    assert "Anträge" in response.text

def test_read_project_detail():
    project_id = PROJECTS[0]["id"]
    response = client.get(f"/antrag/{project_id}")
    assert response.status_code == 200
    assert project_id in response.text

def test_wizard_step_1():
    project_id = PROJECTS[0]["id"]
    response = client.get(f"/wizard/{project_id}/step/1")
    assert response.status_code == 200
    assert "Schritt 1" in response.text

def test_wizard_step_2_scan():
    project_id = PROJECTS[0]["id"]
    response = client.post(f"/wizard/{project_id}/step/2/scan")
    assert response.status_code == 200
    assert "Analyse abgeschlossen" in response.text
