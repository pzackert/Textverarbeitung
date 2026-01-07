
import sys
import time
import requests
import logging

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BackendVerifier")

BASE_URL = "http://localhost:8000"

def check_health():
    try:
        r = requests.get(f"{BASE_URL}/")
        return r.status_code == 200
    except:
        return False

def wait_for_server(timeout=30):
    start = time.time()
    logger.info("Waiting for server...")
    while time.time() - start < timeout:
        if check_health():
            logger.info("Server is UP.")
            return True
        time.sleep(1)
    logger.error("Server timeout.")
    return False

def verify_tc01_auto_load():
    logger.info("=== Executing TC-01: Auto-Load & Identity ===")
    
    # Poll Status
    max_retries = 20
    for i in range(max_retries):
        try:
            r = requests.get(f"{BASE_URL}/api/rag/global/status")
            data = r.json()
            status = data.get("status")
            chunks = data.get("chunks", 0)
            logger.info(f"Poll {i+1}: Status={status}, Chunks={chunks}")
            
            if status == "ready" and chunks > 0:
                logger.info(f"✅ TC-01 Success: RAG Ready with {chunks} chunks.")
                return True
        except Exception as e:
            logger.warning(f"Poll failed: {e}")
        
        time.sleep(2)
        
    logger.error("❌ TC-01 Failed: RAG did not become ready or empty chunks.")
    return False

def verify_tc04_resilience():
    logger.info("=== Executing TC-04: Chat Resilience (Wer bist du?) ===")
    
    # 1. Create Chat
    try:
        r = requests.post(f"{BASE_URL}/api/chats/global")
        if r.status_code != 200:
            logger.error(f"Failed to create chat: {r.text}")
            return False
        chat_id = r.json()["id"]
        logger.info(f"Chat created: {chat_id}")
        
        # 2. Send Message
        payload = {"message": "Wer bist du?"}
        r_msg = requests.post(f"{BASE_URL}/api/chats/global/{chat_id}/message", json=payload)
        
        logger.info(f"Chat Response Code: {r_msg.status_code}")
        
        if r_msg.status_code == 200:
            resp_json = r_msg.json()
            answer = resp_json.get("assistant_message", {}).get("content", "")
            sources = resp_json.get("assistant_message", {}).get("sources", [])
            logger.info(f"Answer: {answer}")
            logger.info(f"Sources: {sources}")
            
            # TC-11 Check: Source Name
            source_found = any(s.get("document") == "herbert.txt" for s in sources)
            if "Herbert" in answer and source_found:
                logger.info("✅ TC-11 Success: Answer mentions Herbert & Source is herbert.txt")
            else:
                logger.warning(f"⚠️ TC-11 Partial: Answer or Source missing. Got {len(sources)} sources.")
            
            logger.info(f"✅ TC-04 Success: Server responded 200 OK.")
            return True
        elif r_msg.status_code in [500, 503]:
            logger.error(f"❌ TC-04 Failed: Server returned {r_msg.status_code} Error.")
            return False
        else:
            logger.warning(f"TC-04 Warning: Unexpected status {r_msg.status_code}")
            return False

    except Exception as e:
        logger.error(f"❌ TC-04 Exception: {e}")
        return False

if __name__ == "__main__":
    if not wait_for_server():
        sys.exit(1)
        
    success = True
    success &= verify_tc01_auto_load()
    success &= verify_tc04_resilience()
    
    if success:
        logger.info("\n🎉 ALL BACKEND TESTS PASSED.")
        sys.exit(0)
    else:
        logger.error("\n💥 SOME TESTS FAILED.")
        sys.exit(1)
