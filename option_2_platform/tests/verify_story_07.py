import requests
import time
import sys
import os

BASE_URL = "http://localhost:8000"

def create_project(name, description):
    print(f"Creating project '{name}'...")
    payload = {"name": name, "description": description, "funding_amount": 1000}
    res = requests.post(f"{BASE_URL}/api/projects/", json=payload)
    if res.status_code not in [200, 201]:
        print(f"Failed to create project {name}: {res.status_code} {res.text}")
        sys.exit(1)
    return res.json()["id"]

def create_dummy_file(filename, content):
    with open(filename, "w") as f:
        f.write(content)
    return filename

def upload_file_to_project(project_id, filename):
    print(f"Uploading {filename} to project {project_id}...")
    with open(filename, "rb") as f:
        files = {"file": (filename, f, "text/plain")}
        res = requests.post(f"{BASE_URL}/api/ingest/project/{project_id}", files=files)
        if res.status_code not in [200, 201]:
            print(f"Upload failed: {res.status_code} {res.text}")
            sys.exit(1)
    print("Upload successful.")

def wait_for_ingestion():
    print("Waiting for ingestion (5s)...")
    time.sleep(5)

def msg_project(project_id, message):
    print(f"Messaging Project {project_id} with: '{message}'")
    payload = {"message": message, "include_rag": True}
    res = requests.post(f"{BASE_URL}/api/chats/project/{project_id}/message", json=payload)
    
    if res.status_code != 200:
        print(f"Message failed: {res.status_code} {res.text}")
        return None
    
    return res.json()["assistant_message"]["content"]

def main():
    # 1. Setup Data
    secret_a = "Projekt A Geheimnis: Der Code ist APFEL."
    secret_b = "Projekt B Geheimnis: Der Code ist BANANE."
    
    file_a = create_dummy_file("secret_proj_a.txt", secret_a)
    file_b = create_dummy_file("secret_proj_b.txt", secret_b)

    try:
        # 2. Create Projects
        pid_a = create_project("Test Projekt A", "Contains Apple Secret")
        pid_b = create_project("Test Projekt B", "Contains Banana Secret")
        
        # 3. Ingest Data
        upload_file_to_project(pid_a, file_a)
        upload_file_to_project(pid_b, file_b)
        wait_for_ingestion()

        # 4. Verify Identity (Self-Check)
        ans_a = msg_project(pid_a, "Wie lautet der Code?")
        if not ans_a or "APFEL" not in ans_a:
            print(f"❌ FAILURE: Project A does not know its own secret. Answer: {ans_a}")
            sys.exit(1)
        print("✅ Project A knows APFEL.")

        ans_b = msg_project(pid_b, "Wie lautet der Code?")
        if not ans_b or "BANANE" not in ans_b:
            print(f"❌ FAILURE: Project B does not know its own secret. Answer: {ans_b}")
            sys.exit(1)
        print("✅ Project B knows BANANE.")

        # 5. Verify Isolation (Leak Test)
        print("\n--- Testing Leakage ---")
        
        # Ask A about B
        leak_a = msg_project(pid_a, "Wie lautet der Code von Projekt B (Banane)?")
        if "BANANE" in leak_a:
             print(f"❌ CRITICAL FAILURE: Project A knows Project B's secret! Answer: {leak_a}")
             sys.exit(1)
        print("✅ Project A does NOT know about BANANE.")

        # Ask B about A
        leak_b = msg_project(pid_b, "Wie lautet der Code von Projekt A (Apfel)?")
        if "APFEL" in leak_b:
             print(f"❌ CRITICAL FAILURE: Project B knows Project A's secret! Answer: {leak_b}")
             sys.exit(1)
        print("✅ Project B does NOT know about APFEL.")
        
        print("\n✅ SUCCESS: Projects are strictly isolated.")

    finally:
        # Cleanup
        if os.path.exists(file_a): os.remove(file_a)
        if os.path.exists(file_b): os.remove(file_b)

if __name__ == "__main__":
    main()
