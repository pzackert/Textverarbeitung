import requests
import json
import time
import os

BASE_URL = "http://127.0.0.1:8000/api"
SECRET_FILENAME = "secret_joachim.txt"
SECRET_CONTENT = "Das streng geheime Geheimnis ist: Joachim trägt heute einen Hut mit einer rosa Schleife."
QUERY_TEXT = "Was trägt Joachim heute?"

def step(msg):
    print(f"\n[STEP] {msg}")

def check_chat_answer(question, should_know=True):
    # Create a chat session
    resp = requests.post(f"{BASE_URL}/chats/global/create")
    if not resp.ok:
        print(f"FAILED to create chat: {resp.text}")
        return False
    chat_id = resp.json()["chat_id"]
    
    # Send message
    payload = {"message": question, "include_rag": True}
    print(f"Asking: '{question}' (Expect Knowledge: {should_know})")
    resp = requests.post(f"{BASE_URL}/chats/global/{chat_id}/message", json=payload)
    
    if not resp.ok:
        print(f"FAILED chat request: {resp.text}")
        return False
        
    data = resp.json()
    answer = data["assistant_message"]["content"]
    print(f"Answer: {answer}")
    
    # Simple keyword check
    has_knowledge = "Schleife" in answer or "Hut" in answer
    
    if should_know and has_knowledge:
        print("SUCCESS: RAG knew the secret.")
        return True
    elif not should_know and not has_knowledge:
        print("SUCCESS: RAG did NOT know the secret (as expected).")
        return True
    else:
        print(f"FAILURE: Knowledge mismatch. Expected {should_know}, Got {has_knowledge}")
        return False

def run_test():
    # 1. Create File
    step("Creating secret file...")
    with open(SECRET_FILENAME, "w") as f:
        f.write(SECRET_CONTENT)
        
    # 2. Upload
    step("Uploading file...")
    with open(SECRET_FILENAME, "rb") as f:
        files = {"file": f}
        resp = requests.post(f"{BASE_URL}/settings/global-knowledge/upload", files=files)
        
    if resp.ok:
        print(f"Upload OK: {resp.json()}")
    else:
        print(f"Upload FAILED: {resp.text}")
        return

    # Allow slight delay for ingestion (though it should be sync based on API)
    time.sleep(2)

    # 3. Query (Should Know)
    step("Verifying Knowledge (Should Know)...")
    if not check_chat_answer(QUERY_TEXT, should_know=True):
        print("ABORTING: RAG ingestion failed.")
        return

    # 4. Delete
    step("Deleting file...")
    resp = requests.delete(f"{BASE_URL}/settings/global-knowledge/{SECRET_FILENAME}")
    if resp.ok:
        print("Delete OK")
    else:
        print(f"Delete FAILED: {resp.text}")
        return
        
    time.sleep(2)

    # 5. Query (Should NOT Know)
    step("Verifying Amnesia (Should NOT Know)...")
    check_chat_answer(QUERY_TEXT, should_know=False)

    # Cleanup local file
    if os.path.exists(SECRET_FILENAME):
        os.remove(SECRET_FILENAME)

if __name__ == "__main__":
    run_test()
