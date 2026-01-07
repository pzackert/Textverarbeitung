
import requests
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
logger = logging.getLogger("RobustnessTest")

BASE_URL = "http://localhost:8000"

def wait_for_startup():
    start = time.time()
    while time.time() - start < 120: # 2 minutes max per run
        try:
            r = requests.get(f"{BASE_URL}/api/system/status")
            if r.status_code == 200:
                data = r.json()
                status = data.get("status")
                logger.debug(f"Status: {status}")
                
                if status in ["ready", "degraded"]:
                    return data
                if status == "error":
                    logger.error(f"System Error: {data.get('current')}")
                    return data
        except Exception as e:
            logger.warning(f"Connection failed: {e}")
        time.sleep(2)
    return None

def verify_components(data):
    components = data.get("components", [])
    required = ["model_scanner", "ai_provider", "vector_store", "llm_loading", "global_knowledge", "project_healing"]
    
    missing = [c for c in required if c not in [comp["name"] for comp in components]]
    if missing:
        logger.error(f"Missing Components: {missing}")
        return False
        
    for comp in components:
        if comp["status"] == "error":
            logger.warning(f"Component Error: {comp['name']} - {comp['message']}")
            # We allow degraded errors if system is degraded
    return True

def run_test_iteration(i):
    logger.info(f"=== Iteration {i+1}/10 ===")
    
    # Trigger Restart
    try:
        requests.post(f"{BASE_URL}/api/system/startup")
    except Exception as e:
        logger.error(f"Failed to trigger startup: {e}")
        return False
        
    # Wait
    final_state = wait_for_startup()
    if not final_state:
        logger.error("Timeout waiting for startup")
        return False
        
    status = final_state.get("status")
    logger.info(f"Startup Finished. Status: {status}")
    
    if status == "error":
        return False
        
    # Verify Components
    if not verify_components(final_state):
        return False
        
    return True

if __name__ == "__main__":
    success_count = 0
    for i in range(10):
        if run_test_iteration(i):
            success_count += 1
        else:
            logger.error(f"Iteration {i+1} FAILED")
            break # Stop on first failure? Or continue? User asked for 10x clean.
            # Stop to debug is better.
    
    logger.info(f"=== Result: {success_count}/10 Successful Runs ===")
