
import requests
import json
import time
import sys
import os

BASE_URL = "http://localhost:8000"

def log(msg, status="INFO"):
    print(f"[{time.strftime('%H:%M:%S')}] [{status}] {msg}")

def check(response, expected_code=200, name="Request"):
    if response.status_code == expected_code:
        log(f"{name} Passed ({response.status_code})", "SUCCESS")
        return True
    else:
        log(f"{name} FAILED ({response.status_code}): {response.text[:200]}", "ERROR")
        return False

def verify_system():
    log("=== 1. System Start (US-1.1) ===")
    resp = requests.get(f"{BASE_URL}/api/system/status")
    if not check(resp, 200, "System Status"): return False
    data = resp.json()
    if data["status"] not in ["ready", "degraded", "initializing"]:
        log(f"System status is {data['status']}", "WARNING")
    
    log("=== 2. Global Chat (US-2.x) ===")
    # 2.1 Create Chat
    resp = requests.post(f"{BASE_URL}/api/chats/global/create", json={}) # No title needed in create logic seen
    if not check(resp, 201, "Create Global Chat"): return False
    chat_id = resp.json()["chat_id"]
    
    # 2.3 Ask Question (Mock or Real)
    log("Sending global message...")
    resp = requests.post(f"{BASE_URL}/api/chats/global/{chat_id}/message", 
                         json={"message": "Hallo, wer bist du?", "include_rag": False}) # use 'message' key, valid payload
    check(resp, 200, "Global Chat Message")

    # 2.4 Delete Chat
    resp = requests.delete(f"{BASE_URL}/api/chats/global/{chat_id}")
    check(resp, 200, "Delete Global Chat")

    log("=== 3. Projects (US-3.x) & Documents (US-6.x) ===")
    # 3.2 Create Project (Frontend Route, Form Data)
    unique_name = f"Verification_Project_{int(time.time())}"
    proj_data = {
        "name": unique_name,
        "applicant": "Test GmbH",
        "funding_amount": 50000,
        "description": "Automated Test"
    }
    # Note: Frontend router is at /projects (root), not /api/projects
    resp = requests.post(f"{BASE_URL}/projects", data=proj_data, allow_redirects=True)
    if not check(resp, 200, "Create Project (Form)"): return False
    
    # Extract ID from HTML list
    # We look for the link to /projects/{id}/review inside the HTML
    import re
    # Pattern: href="/projects/([^"]+)/review".*?Verification_Project_...
    # Simple search for the name, then find the closest link before/after?
    # Or just search for the specific link structure if we know the list renders it.
    
    # HTML structure: <tr ...> ... Name ... <a href="/projects/ID/review"> ... </tr>
    # We use DOTALL to match across lines
    pattern = rf'<tr[^>]*>.*?{unique_name}.*?href="/projects/([^"/]+)/review"'
    match = re.search(pattern, resp.text, re.DOTALL)
    
    # Retry listing if redirect didn't return list (it should)
    if not match:
        resp = requests.get(f"{BASE_URL}/projects")
        match = re.search(pattern, resp.text, re.DOTALL)
        
    if match:
        project_id = match.group(1)
        log(f"Created Project ID: {project_id}")
    else:
        # Debug dump if fail
        log("Could not extract Project ID from HTML. Dumping fragment...", "ERROR")
        log(resp.text[:1000] + "...", "DEBUG")
        return False

    # 6.1 Upload Document (Frontend Route for Upload: POST /projects/{id}/upload)
    # Using the frontend upload route which calls save_document
    # This route expects 'file' in multipart form
    with open("verify_doc.txt", "w") as f:
        f.write("Der Antragsteller lautet Verification Project GmbH. Die Foerdersumme betraegt 50000 Euro.")
    
    with open("verify_doc.txt", "rb") as f:
        files = {"file": ("verify_doc.txt", f, "text/plain")}
        resp = requests.post(f"{BASE_URL}/projects/{project_id}/upload", files=files) 
    check(resp, 200, "Upload Document")
    
    # Trigger RAG Ingest manually just in case async is slow
    requests.post(f"{BASE_URL}/api/projects/{project_id}/rag/ingest")
    # It is synchronous, but wait a bit for file system sync
    time.sleep(2)

    log("=== 4. Project Chat (US-4.x) ===")
    # 4.3 Chat with Project
    # Query matching the text exactly
    resp = requests.post(f"{BASE_URL}/api/chats/project/{project_id}/message", 
                         json={"message": "Wie lautet der Antragsteller?", "include_rag": True})
    check(resp, 200, "Project Chat Message")
    
    log("=== 5. Criteria Check (US-5.x) ===")
    # 5.1 List Criteria
    resp = requests.get(f"{BASE_URL}/api/criteria")
    if not check(resp, 200, "List Criteria"): return False
    criteria = resp.json()
    if not criteria:
        log("No criteria found to test", "WARNING")
    else:
        crit_id = criteria[0]["id"]
        log(f"Testing Criterion: {crit_id}")
        
        # 5.2 Evaluate Single Criterion
        # Route: /api/projects/{project_id}/criteria/{criterion_id}/evaluate
        resp = requests.post(f"{BASE_URL}/api/projects/{project_id}/criteria/{crit_id}/evaluate")
        check(resp, 200, "Evaluate Criterion")
        
        # 5.3 Evaluate All (Batch)
        # Route: /api/projects/{project_id}/criteria/evaluate-all
        resp = requests.post(f"{BASE_URL}/api/projects/{project_id}/criteria/evaluate-all")
        check(resp, 200, "Evaluate All Criteria")

    log("=== Cleanup (US-3.5) ===")
    # 3.5 Delete Project
    # Route: DELETE /projects/{id} (Frontend Route)
    resp = requests.delete(f"{BASE_URL}/projects/{project_id}")
    check(resp, 200, "Delete Project")
    
    os.remove("verify_doc.txt")
    log("Verification Complete", "SUCCESS")
    return True

if __name__ == "__main__":
    try:
        if verify_system():
            sys.exit(0)
        else:
            sys.exit(1)
    except Exception as e:
        log(f"Script Crash: {e}", "CRITICAL")
        sys.exit(1)
