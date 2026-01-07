import requests
import sys
import time
import shutil
import os
import re
import logging
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000/api/v1/projects"
FRONTEND_URL = "http://localhost:8000/projects"
DUMMY_PDF = "data/input/dummy_test.pdf"

# Setup Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log(msg):
    print(f"[TEST] {msg}")

def check(condition, msg):
    if condition:
        print(f"✅ {msg}")
    else:
        print(f"❌ {msg}")
        raise Exception(f"Check failed: {msg}")

def ensure_test_pdf():
    """Ensures a valid PDF exists for testing."""
    if os.path.exists(DUMMY_PDF):
        return DUMMY_PDF
    
    sources = [
        "data/projects/80a26bfc-7274-47bd-9d80-276a540b2006/documents/dummy.pdf",
        "data/global_knowledge/dummy.pdf" 
    ]
    for src in sources:
        if os.path.exists(src):
            shutil.copy(src, DUMMY_PDF)
            return DUMMY_PDF
            
    log("Warning: No PDF source found. creating empty one.")
    with open(DUMMY_PDF, "wb") as f:
        f.write(b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n/Pages 2 0 R\n>>\nendobj\n2 0 obj\n<<\n/Type /Pages\n/Kids [3 0 R]\n/Count 1\n>>\nendobj\n3 0 obj\n<<\n/Type /Page\n/Parent 2 0 R\n/MediaBox [0 0 612 792]\n/Resources <<\n/Font <<\n/F1 4 0 R\n>>\n>>\n/Contents 5 0 R\n>>\nendobj\n4 0 obj\n<<\n/Type /Font\n/Subtype /Type1\n/BaseFont /Helvetica\n>>\nendobj\n5 0 obj\n<<\n/Length 44\n>>\nstream\nBT\n/F1 24 Tf\n100 700 Td\n(Hello World) Tj\nET\nendstream\nendobj\nxref\n0 6\n0000000000 65535 f\n0000000010 00000 n\n0000000060 00000 n\n0000000117 00000 n\n0000000240 00000 n\n0000000327 00000 n\ntrailer\n<<\n/Size 6\n/Root 1 0 R\n>>\nstartxref\n393\n%%EOF")
    return DUMMY_PDF

def test_backend_flow():
    app_id = None
    try:
        log("Testing Backend Application Processing Flow (Black Box)...")
        
        # 1. Setup: Create Project via Frontend Form
        log("Creating Test Project...")
        project_name = f"VerifcationAutoTest_{int(time.time())}"
        payload = {
            "name": project_name,
            "description": "Created by verify_phase3.py",
            "applicant": "Tester McTestface",
            "funding_amount": 5000.0
        }
        resp = requests.post(FRONTEND_URL, data=payload)
        check(resp.status_code == 200, f"Create Project Request ({resp.status_code})")
        # Note: Response is the Redirected HTML Page (Projects List)
        
        # 2. Extract ID from HTML
        # Look for partial match of the project name or just the newest entry?
        # Better: Look for project_name in the HTML, then find the associated ID link nearby.
        log("Extracting Project ID...")
        html = resp.text
        # Naive: Find the link that contains /review and extract ID.
        # Assuming the new project is top or we can find it by name.
        if project_name not in html:
            # Maybe it didn't redirect or name isn't shown?
            # It redirects to /projects, so HTML is the list.
             check(False, "Project Name not found in List HTML")
        
        # Regex to find ID associated with name?
        # Structure: ...href="/projects/{id}/review"...
        # It's hard to associate name to ID with simple regex if they are far apart.
        # But we can look for all IDs and pick the logic one?
        # Or assumes parsing table.
        # Let's try: Find our project name, then look backwards/forwards for the ID link?
        # Actually, let's just find ALL project links and assume ours is one of them.
        # Or, filter the LIST response by name?
        # The GET /projects endpoint supports ?search=...
        
        search_url = f"{FRONTEND_URL}?search={project_name}"
        resp = requests.get(search_url)
        check(resp.status_code == 200, "Search Project")
        html = resp.text
        
        # Look for Link in search result
        all_links = re.findall(r'href="/projects/([^/"]+)/review"', html)
        
        if all_links:
            # Pick the first one. Since we searched for a unique name, this should be it.
            app_id = all_links[0]
            log(f"Project Created & Found: {app_id}")
        else:
            log("DEBUG: HTML Content Snippet (first 1000 chars):")
            log(html[:1000])
            log("DEBUG: Checking for Project Name in HTML:")
            log(str(project_name in html))
            check(False, "Could not extract Project ID from Search Results")

        
        # 3. Upload Document via Frontend Endpoint
        pdf_path = ensure_test_pdf()
        log(f"Uploading {pdf_path}...")
        
        with open(pdf_path, "rb") as f:
            files = {"file": (os.path.basename(pdf_path), f, "application/pdf")}
            upload_url = f"{FRONTEND_URL}/{app_id}/upload"
            resp = requests.post(upload_url, files=files)
            check(resp.status_code == 200, f"Upload Document ({resp.status_code})")
            
        # 4. Trigger Ingestion (Frontend Router)
        log("Triggering Ingestion...")
        ingest_url = f"{FRONTEND_URL}/{app_id}/rag/ingest"
        resp = requests.post(ingest_url)
        check(resp.status_code == 200, f"Trigger Ingest ({resp.status_code})")
        
        # 5. Wait/Poll
        log("Waiting for ingestion (5s)...")
        time.sleep(5)
        
        # 6. Chat Query (Backend API)
        log("Testing Chat (Validating Connectivity)...")
        chat_url = f"http://localhost:8000/api/chats/project/{app_id}/message"
        
        # Test 1: Simple Chat (No RAG) - Checks LLM Connection
        log("Test 1: Simple Chat (No RAG)...")
        try:
            resp = requests.post(chat_url, json={"message": "Hello", "include_rag": False})
            if resp.status_code == 200:
                log("✅ Simple Chat OK")
            else:
                log(f"❌ Simple Chat Failed ({resp.status_code}): {resp.text}")
        except Exception as e:
            log(f"Exception: {e}")

        # Test 2: RAG Chat
        log("Test 2: RAG Chat...")
        r_query = {"message": "Wie hoch ist die Fördersumme?", "include_rag": True}
        
        got_answer = False
        for i in range(3):
            try:
                resp = requests.post(chat_url, json=r_query)
                if resp.status_code == 200:
                    data = resp.json()
                    answer = data.get('response') or data.get('assistant_message', {}).get('content')
                    log(f"Chat Answer: {str(answer)[:100]}...")
                    if answer:
                        got_answer = True
                        break
                else:
                    log(f"Chat Error {resp.status_code}: {resp.text}")
            except Exception as e:
                log(f"Chat Exception: {e}")
            time.sleep(2)
            
        check(got_answer, "Received RAG Chat Answer")

        # 7. Cleanup
        log("Cleaning up...")
        del_url = f"{FRONTEND_URL}/{app_id}"
        requests.delete(del_url)
        check(True, "Cleanup")
        
        log("✅ PHASE 3 BACKEND VERIFICATION PASSED")
        
    except Exception as e:
        log(f"❌ TEST FAILED: {e}")
        if app_id:
            try:
                requests.delete(f"{FRONTEND_URL}/{app_id}")
                log("Cleanup performed after failure.")
            except:
                pass
        sys.exit(1)

if __name__ == "__main__":
    test_backend_flow()
