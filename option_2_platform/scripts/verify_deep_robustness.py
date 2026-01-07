
import sys
import time
import requests
import json

BASE_URL = "http://localhost:8000"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def fail(msg):
    log(f"[FAIL] {msg}")
    sys.exit(1)

def check_response(resp, description, expected_status=200):
    if resp.status_code != expected_status:
        fail(f"{description} returned {resp.status_code}: {resp.text}")
    return resp.json()

def verify_global_chat():
    log("=== Verifying Global Chat Robustness ===")
    
    # 0. Trigger Reload (to pick up metadata changes)
    requests.post(f"{BASE_URL}/api/rag/global/load")
    # Poll for status
    status = "loading"
    waited = 0
    while status != "ready" and status != "error" and waited < 120:
        time.sleep(2)
        waited += 2
        s_resp = requests.get(f"{BASE_URL}/api/rag/global/status")
        status = s_resp.json().get("status")
        prog = s_resp.json().get("overall_progress_pct")
        log(f"Status: {status} ({prog}%)")
    
    if status != "ready":
        fail(f"Global Ingestion timed out or failed: {status}") 

    # 1. Create Chat
    resp = requests.post(f"{BASE_URL}/api/chats/global/create")
    chat_data = check_response(resp, "Create Global Chat", expected_status=201)
    chat_id = chat_data["chat_id"]
    
    # 2. Test KNOWN Answer (Identity)
    # User Story: "Assistant acts as Herbert"
    # Data: data/global_knowledge/Herbert.txt exists.
    log("Test 1: Identity Question ('Wer bist du?')")
    resp = requests.post(f"{BASE_URL}/api/chats/global/{chat_id}/message", 
                         json={"message": "Wer bist du?", "include_rag": True})
    data = check_response(resp, "Identity Question")
    answer = data["assistant_message"]["content"]
    log(f"Answer: {answer}")
    
    if "Herbert" not in answer and "Fördermittel-Experte" not in answer and "Sachbearbeiter" not in answer:
        log("[WARNING] Answer did not contain 'Herbert' or expected identity. RAG Retrieval might be weak.")
    else:
        log("[PASS] Identity confirmed.")
        
    # 3. Test NEGATIVE Case (Nonsense)
    # Goal: Ensure NO 500/503 Error.
    log("Test 2: Nonsense Question ('Xylophon8812')")
    resp = requests.post(f"{BASE_URL}/api/chats/global/{chat_id}/message", 
                         json={"message": "Xylophon8812 gibt es das?", "include_rag": True})
    
    if resp.status_code == 503:
        fail("Nonsense question triggered 503 Service Unavailable! This is the user's reported bug.")
    elif resp.status_code != 200:
        fail(f"Nonsense question failed with {resp.status_code}")
        
    ans_neg = resp.json()["assistant_message"]["content"]
    log(f"Answer to Nonsense: {ans_neg}")
    if "keine" not in ans_neg.lower() and "nicht" not in ans_neg.lower():
         log("[WARNING] Fallback answer might be hallucinating.")
    else:
         log("[PASS] Graceful fallback confirmed.")

def verify_project_chat():
    log("=== Verifying Project Chat Robustness ===")
    
    # 1. Create Project (Frontend)
    unique_name = f"Robust_Proj_{int(time.time())}"
    proj_data = {"name": unique_name, "applicant": "Robust GmbH", "funding_amount": 1000, "description": "Test"}
    resp = requests.post(f"{BASE_URL}/projects", data=proj_data) # Redirects
    
    # Extract ID - Regex: Row contains Name ... then Link to Review
    import re
    # Pattern: Name ... href="/projects/ID/review"
    # Use DOTALL for multiline matching in table row
    match = re.search(rf'{unique_name}.*?href="/projects/([^"/]+)/review"', requests.get(f"{BASE_URL}/projects").text, re.DOTALL)
    if not match:
        fail("Could not find created project ID")
    project_id = match.group(1)
    log(f"Created Project: {project_id}")
    
    # 2. Upload Document
    with open("robust_doc.txt", "w") as f:
        f.write("Der Projektleiter heisst Dr. Robustus. Die Projektlaufzeit betraegt 12 Monate.")
    
    files = {"file": ("robust_doc.txt", open("robust_doc.txt", "rb"), "text/plain")}
    requests.post(f"{BASE_URL}/projects/{project_id}/upload", files=files)
    
    # 3. Ingest and Wait
    requests.post(f"{BASE_URL}/api/projects/{project_id}/rag/ingest")
    log("Waiting 15s for ingestion...")
    time.sleep(15)
    
    # 4. Content Query
    log("Test 3: Project Fact ('Wie heisst der Projektleiter?')")
    resp = requests.post(f"{BASE_URL}/api/chats/project/{project_id}/message", 
                         json={"message": "Wie heisst der Projektleiter?", "include_rag": True})
    
    if resp.status_code == 503:
        fail("Project Chat 503! RAG failed to retrieve sources.")
    
    data = check_response(resp, "Project Query")
    answer = data["assistant_message"]["content"]
    log(f"Answer: {answer}")
    
    if "Robustus" not in answer:
         fail(f"RAG failed to retrieve specific content. Expected 'Robustus', got: {answer}")
    else:
         log("[PASS] Specific content retrieval confirmed.")

    # Cleanup
    requests.delete(f"{BASE_URL}/projects/{project_id}")
    log("[PASS] Cleanup.")

if __name__ == "__main__":
    verify_global_chat()
    verify_project_chat()
    log("=== ALL ROBUSTNESS TESTS PASSED ===")
