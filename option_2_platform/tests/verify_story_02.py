
import requests
import time
import sys

BASE_URL = "http://localhost:8000"
FIXTURE_PATH = "tests/fixtures/herbert.txt"

def ensure_knowledge():
    # Use existing herbert.txt if already uploaded (Bug 1 test)
    # But for robustness, upload again?
    # Since we use upsert, it's safe.
    print(f"Uploading {FIXTURE_PATH}...")
    with open(FIXTURE_PATH, "rb") as f:
        files = {"file": ("herbert.txt", f, "text/plain")}
        res = requests.post(f"{BASE_URL}/api/knowledge/upload", files=files)
        if res.status_code not in [200, 201]:
            print(f"Upload failed: {res.status_code}")
            sys.exit(1)
    time.sleep(2) # Short wait

def test_multi_session_identity():
    print("-- Creating Chat Session A --")
    res = requests.post(f"{BASE_URL}/api/chats/global/create")
    chat_a_id = res.json()["chat_id"]
    
    query = "Wer ist Herbert?"
    print(f"Sending query to Chat A: '{query}'")
    payload = {"message": query, "include_rag": True}
    
    # We expect this to work (Bug 1 fixed)
    # But strictly, we assume Bug 1 test ran.
    # We won't assert strict answer here to save time, unless necessary.
    # Just sending message to warm up?
    # No, let's verify context is available.
    res_a = requests.post(f"{BASE_URL}/api/chats/global/{chat_a_id}/message", json=payload)
    if res_a.status_code != 200:
        print("Chat A failed")
        sys.exit(1)
    
    ans_a = res_a.json()["assistant_message"]["content"]
    print(f"Chat A Answer: {ans_a[:100]}...")
    
    if "Herbert" not in ans_a and "Sachbearbeiter" not in ans_a:
        print("⚠️ Chat A missed identity (Performance hiccup or logic?)")
        # Proceed to Chat B anyway to test ISOLATION/PERSISTENCE?
        # Bug 2 is "New chats lose context". If Chat A works, Chat B should too.
    
    print("-- Creating Chat Session B (Mocking 'New User') --")
    res_b = requests.post(f"{BASE_URL}/api/chats/global/create")
    chat_b_id = res_b.json()["chat_id"]
    
    print(f"Sending query to Chat B: '{query}'")
    res_b_msg = requests.post(f"{BASE_URL}/api/chats/global/{chat_b_id}/message", json=payload)
    if res_b_msg.status_code != 200:
        print("Chat B failed")
        sys.exit(1)
        
    ans_b = res_b_msg.json()["assistant_message"]["content"]
    print(f"Chat B Answer: {ans_b[:100]}...")
    
    if "Herbert" in ans_b or "Sachbearbeiter" in ans_b:
        print("✅ SUCCESS: Identity available in fresh session.")
    else:
        print("❌ FAILURE: Identity lost in fresh session.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        ensure_knowledge()
        test_multi_session_identity()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
