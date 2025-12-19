import requests
import time
import json

BASE_URL = "http://localhost:8000"
PROJECT_ID = "test_project" # We might need a real ID, checking registry first
# Based on file listing from previous turns, I saw a project ID in the URL: "8209d44a"
# Let's try to list projects first to get a valid ID.

def get_valid_project_id():
    try:
        # Assuming registry is at data/input/registry.json, we can just read it or hit the list endpoint (parsing HTML is hard)
        # Let's rely on the hardcoded ID from the user prompt: "8209d44a"
        # If it doesn't exist, we might fail, but let's try.
        return "8209d44a"
    except:
        return None

def test_rag_workflow():
    project_id = get_valid_project_id()
    print(f"Testing with Project ID: {project_id}")

    # 1. Ingest (Bulk)
    print("\n--- 1. Triggering Ingestion ---")
    resp = requests.post(f"{BASE_URL}/api/projects/{project_id}/rag/ingest")
    print(f"Ingest Status: {resp.status_code}")
    print(resp.json())
    
    # Wait for background task (naive wait)
    print("Waiting 5s for ingestion...")
    time.sleep(5)

    # 2. Chat (Check Context)
    print("\n--- 2. Chat Query (With RAG) ---")
    # Using the new JSON endpoint structure I added
    payload = {
        "message": "Was ist das Thema des Antrags?", 
        "include_rag": True
    }
    try:
        resp = requests.post(f"{BASE_URL}/api/projects/{project_id}/chat", json=payload)
        print(f"Chat Status: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"Response: {data.get('response')[:100]}...") # Print start
            print(f"Sources: {len(data.get('sources', []))}")
            if len(data.get('sources', [])) > 0:
                print("SUCCESS: Context found.")
            else:
                print("WARNING: No context found (Ingestion might be slow or empty docs).")
        else:
            print("Chat Failed.")
    except Exception as e:
        print(f"Chat Request Failed: {e}")

    # 3. Cleanup
    print("\n--- 3. Cleanup RAG ---")
    resp = requests.delete(f"{BASE_URL}/api/projects/{project_id}/rag")
    print(f"Cleanup Status: {resp.status_code}")
    print(resp.json())

    # 4. Chat (Check Context Gone)
    print("\n--- 4. Chat Query (After Cleanup) ---")
    try:
        resp = requests.post(f"{BASE_URL}/api/projects/{project_id}/chat", json=payload)
        if resp.status_code == 200:
            data = resp.json()
            print(f"Sources: {len(data.get('sources', []))}")
            if len(data.get('sources', [])) == 0:
                print("SUCCESS: Context cleared.")
            else:
                print("FAILURE: Context still exists!")
    except Exception as e:
        print(f"Chat Request Failed: {e}")

if __name__ == "__main__":
    test_rag_workflow()
