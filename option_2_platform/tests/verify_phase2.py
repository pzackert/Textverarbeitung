import requests
import sys

BASE_URL = "http://localhost:8000/api"

def log(msg):
    print(f"[TEST] {msg}")

def check(condition, msg):
    if condition:
        print(f"✅ {msg}")
    else:
        print(f"❌ {msg}")
        sys.exit(1)

def test_crud():
    log("Testing Application CRUD...")
    
    # 1. Create
    payload = {
        "title": "Verif App",
        "applicant": "Test User",
        "funding_request": 5000.0,
        "description": "Test Description"
    }
    resp = requests.post(f"{BASE_URL}/applications", json=payload)
    check(resp.status_code == 200, "Create App (200 OK)")
    data = resp.json()
    app_id = data["id"]
    check(data["title"] == "Verif App", "Title checked")
    
    # 2. List
    resp = requests.get(f"{BASE_URL}/applications")
    check(resp.status_code == 200, "List Apps (200 OK)")
    apps = resp.json()
    check(any(a["id"] == app_id for a in apps), "New app found in list")
    
    # 3. Upload Doc
    # mock file
    files = {'file': ('test.txt', b'Hello World')}
    resp = requests.post(f"{BASE_URL}/applications/{app_id}/documents", files=files)
    check(resp.status_code == 200, "Upload Doc (200 OK)")
    
    # 4. Get Detail (Verify Doc)
    resp = requests.get(f"{BASE_URL}/applications/{app_id}")
    app_detail = resp.json()
    check(len(app_detail["documents"]) == 1, "Document count is 1")
    check(app_detail["documents"][0]["filename"] == "test.txt", "Filename checked")
    
    # 5. Update
    patch = {"status": "submitted"}
    resp = requests.patch(f"{BASE_URL}/applications/{app_id}", json=patch)
    check(resp.status_code == 200, "Update App (200 OK)")
    check(resp.json()["status"] == "submitted", "Status updated")
    
    # 6. Delete
    resp = requests.delete(f"{BASE_URL}/applications/{app_id}")
    check(resp.status_code == 200, "Delete App (200 OK)")
    
    # 7. Verify Delete
    resp = requests.get(f"{BASE_URL}/applications/{app_id}")
    check(resp.status_code == 404, "Get Deleted App (404)")

if __name__ == "__main__":
    try:
        test_crud()
        log("ALL PHASE 2 TESTS PASSED")
    except Exception as e:
        log(f"TEST FAILED: {e}")
        sys.exit(1)
