import requests
import time
import sys

BASE_URL = "http://localhost:8000"
FIXTURE_PATH = "tests/fixtures/herbert.txt"

def upload_knowledge():
    print(f"Uploading {FIXTURE_PATH}...")
    with open(FIXTURE_PATH, "rb") as f:
        files = {"file": ("herbert.txt", f, "text/plain")}
        res = requests.post(f"{BASE_URL}/api/knowledge/upload", files=files)
        if res.status_code not in [200, 201]:
            print(f"Upload failed: {res.status_code} {res.text}")
            sys.exit(1)
        print("Upload successful.")

def wait_for_ingestion():
    # In a real system, we might need to poll a job status. 
    # Here we assume synchronous or fast enough async content.
    print("Waiting for RAG ingestion (5s)...")
    time.sleep(5)

def test_chat_identity():
    print("Creating new chat...")
    res = requests.post(f"{BASE_URL}/api/chats/global/create")
    if res.status_code not in [200, 201]:
        print(f"Chat creation failed: {res.status_code}")
        sys.exit(1)
    chat_id = res.json()["chat_id"]
    print(f"Chat ID: {chat_id}")

    query = "Wer ist Herbert?"
    print(f"Sending query: '{query}'")
    
    payload = {"message": query, "include_rag": True}
    res = requests.post(f"{BASE_URL}/api/chats/global/{chat_id}/message", json=payload)
    if res.status_code != 200:
        print(f"Message failed: {res.status_code}")
        sys.exit(1)
    
    data = res.json()
    answer = data["assistant_message"]["content"]
    print(f"Answer: {answer}")

    if "Herbert" in answer and "Sachbearbeiter" in answer:
        print("✅ SUCCESS: Identity confirmed.")
    else:
        print("❌ FAILURE: 'Herbert' or 'Sachbearbeiter' not found in answer.")
        sys.exit(1)

if __name__ == "__main__":
    try:
        upload_knowledge()
        wait_for_ingestion()
        test_chat_identity()
    except Exception as e:
        print(f"Test Error: {e}")
        sys.exit(1)
