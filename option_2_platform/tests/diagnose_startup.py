
import logging
import asyncio
import time
import requests
from src.core.config import load_config
from src.rag.config import RAGConfig
from src.services.model_scanner import scan_all_models
from src.services.system_state import system_state, ComponentStatus

# Setup Console Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("Diagnostics")

async def diagnose_startup():
    logger.info("=== STARTING DIAGNOSTICS ===")
    
    logger.info("[Step 0] Loading Configurations...")
    try:
        raw_config = load_config()
        rag_config = RAGConfig.from_yaml()
        llm_conf = rag_config.llm
        logger.info(f"Config Loaded. Provider: {llm_conf.provider}, Model: {llm_conf.model}")
    except Exception as e:
        logger.error(f"Config Load Failed: {e}")
        return

    logger.info("[Step 1] Scanning Models...")
    try:
        t0 = time.time()
        scan_results = scan_all_models(llm_conf)
        logger.info(f"Scan finished in {time.time()-t0:.2f}s. Found: {len(scan_results) if scan_results else 0} models.")
    except Exception as e:
        logger.error(f"Model Scan Failed: {e}")

    logger.info("[Step 2] Check LM Studio...")
    lm_studio_url = llm_conf.lm_studio.endpoint or "http://127.0.0.1:1234"
    logger.info(f"LM Studio URL: {lm_studio_url}")
    
    try:
        t0 = time.time()
        logger.info("Sending GET request to /v1/models...")
        resp = requests.get(f"{lm_studio_url}/v1/models", timeout=2) # Matching system_state.py timeout
        logger.info(f"Response: {resp.status_code} in {time.time()-t0:.2f}s")
    except Exception as e:
        logger.warning(f"LM Studio Check Failed: {e}")

    logger.info("[Step 3] Check Ollama...")
    ollama_url = llm_conf.ollama.endpoint or "http://localhost:11434"
    logger.info(f"Ollama URL: {ollama_url}")
    try:
        t0 = time.time()
        logger.info("Sending GET request to /api/tags...")
        resp = requests.get(f"{ollama_url}/api/tags", timeout=2)
        logger.info(f"Response: {resp.status_code} in {time.time()-t0:.2f}s")
    except Exception as e:
        logger.warning(f"Ollama Check Failed: {e}")

    logger.info("=== DIAGNOSTICS COMPLETE ===")

if __name__ == "__main__":
    asyncio.run(diagnose_startup())
