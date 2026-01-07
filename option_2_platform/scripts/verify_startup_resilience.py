
import requests
import time
import sys

BASE_URL = "http://localhost:8000"

def check_status():
    try:
        resp = requests.get(f"{BASE_URL}/api/system/status")
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return None

def verify_startup_behavior():
    print("--- Verifying Startup Resilience ---")
    
    # Trigger restart
    try:
        requests.post(f"{BASE_URL}/api/system/startup")
        print("Startup triggered.")
    except: 
        print("Coult not trigger startup.")

    # Wait for stable state
    max_retries = 30
    seen_init = False
    
    for i in range(max_retries):
        status_data = check_status()
        if status_data:
            status = status_data.get("status")
            current = status_data.get("current", "")
            print(f"[{i}] Status: {status} - Current: {current}")
            
            if status == "initializing":
                seen_init = True
            
            if status in ["ready", "degraded", "error"] and seen_init:
                # Check specifics
                components = status_data.get("components_dict", {})
                llm = components.get("llm_model", {})
                projects = components.get("projects", {})
                
                print(f"Final State: {status}")
                print(f"LLM Status: {llm.get('status')} - {llm.get('message')}")
                print(f"Projects Status: {projects.get('status')} - {projects.get('message')}")
                
                return
        time.sleep(2)


if __name__ == "__main__":
    verify_startup_behavior()
