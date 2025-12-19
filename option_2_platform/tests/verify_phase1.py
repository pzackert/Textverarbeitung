import requests
import time
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

def test_system_startup():
    log("Testing System Startup & Status...")
    
    # 1. Trigger Startup
    resp = requests.post(f"{BASE_URL}/system/startup")
    check(resp.status_code == 200, "Startup Triggered (200 OK)")
    
    # 2. Poll Status
    max_retries = 15
    ready = False
    for i in range(max_retries):
        resp = requests.get(f"{BASE_URL}/system/status")
        data = resp.json()
        status = data.get("status")
        log(f"Status poll {i+1}: {status}")
        
        # Verify Schema (Simple check)
        check("components" in data, "Response has 'components'")
        check("ollama" in data["components"], "Response has 'ollama' component")
        
        if status == "ready":
            ready = True
            break
        time.sleep(1)
        
    check(ready, "System reached 'ready' state")

def test_global_chat():
    log("Testing Global Chat...")
    
    # 1. Create Chat
    resp = requests.post(f"{BASE_URL}/chat/global/create")
    check(resp.status_code == 200, "Create Chat (200 OK)")
    chat_id = resp.json().get("chat_id")
    check(chat_id is not None, f"Got chat_id: {chat_id}")
    
    # 2. List Chats
    resp = requests.get(f"{BASE_URL}/chat/global/list")
    check(resp.status_code == 200, "List Chats (200 OK)")
    chats = resp.json()
    check(any(c["chat_id"] == chat_id for c in chats), "New chat found in list")
    
    # 3. Send Message
    msg_payload = {"message": "Hello Test", "use_base_documents": True}
    resp = requests.post(f"{BASE_URL}/chat/global/{chat_id}/message", json=msg_payload)
    check(resp.status_code == 200, "Send Message (200 OK)")
    
    # 4. Get History
    resp = requests.get(f"{BASE_URL}/chat/global/{chat_id}/history")
    history = resp.json().get("messages", [])
    check(len(history) >= 2, "History has at least 2 messages (User + AI)")
    check(history[0]["role"] == "user", "First msg is user")
    check(history[1]["role"] == "assistant", "Second msg is assistant")

if __name__ == "__main__":
    try:
        test_system_startup()
        test_global_chat()
        log("ALL BACKEND TESTS PASSED")
    except Exception as e:
        log(f"TEST FAILED: {e}")
        sys.exit(1)
