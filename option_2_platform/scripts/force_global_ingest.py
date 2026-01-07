
import sys
import time
import requests

BASE_URL = "http://localhost:8000"

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def check(resp, code, msg):
    if resp.status_code != code:
        log(f"[ERROR] {msg} FAILED ({resp.status_code}): {resp.text}")
        return False
    log(f"[SUCCESS] {msg} Passed")
    return True

def force_ingest():
    log("=== Forcing Global RAG Ingestion ===")
    
    # 1. Trigger Load
    resp = requests.post(f"{BASE_URL}/api/rag/global/load")
    if not check(resp, 202, "Trigger Ingestion"): return False
    
    # 2. Poll Status
    status = "loading"
    waited = 0
    while status != "ready" and status != "error" and waited < 60:
        time.sleep(2)
        waited += 2
        resp = requests.get(f"{BASE_URL}/api/rag/global/status")
        data = resp.json()
        status = data.get("status")
        progress = data.get("overall_progress_pct", 0)
        log(f"Status: {status} ({progress}%)")
    
    if status != "ready":
        log(f"[ERROR] Ingestion timed out or failed: {status}")
        return False
        
    log("Ingestion Complete.")
    
    # 3. Verify Retrieval
    log("Verifying Retrieval for 'Wer bist du?'...")
    # Create temp chat
    c_resp = requests.post(f"{BASE_URL}/api/chats/global/create")
    chat_id = c_resp.json()["chat_id"]
    
    # Send message
    m_resp = requests.post(f"{BASE_URL}/api/chats/global/{chat_id}/message", 
                           json={"message": "Wer bist du?", "include_rag": True})
    
    if m_resp.status_code == 200:
        ans = m_resp.json()["assistant_message"]["content"]
        log(f"Answer: {ans}")
        if "Herbert" in ans or "Sachbearbeiter" in ans:
             log("[SUCCESS] RAG Answer Validation Passed (Contains 'Herbert'/'Sachbearbeiter')")
        else:
             log("[WARNING] Answer might be generic. Validation Weak.")
    else:
        log(f"[ERROR] Chat failed: {m_resp.status_code} {m_resp.text}")
        return False
        
    return True

if __name__ == "__main__":
    if force_ingest():
        print("FORCE INGEST SUCCESS")
        sys.exit(0)
    else:
        print("FORCE INGEST FAILED")
        sys.exit(1)
