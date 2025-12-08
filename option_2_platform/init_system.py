import subprocess
import time
import requests
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

def init_llm_service() -> bool:
    """
    Initialize LLM Service (Ollama).
    Checks if running, if not starts it.
    Checks if model is loaded, if not pulls it.
    """
    # 1. Check if Ollama is running
    try:
        requests.get("http://localhost:11434", timeout=2)
        logger.info("✅ Ollama service is running")
    except requests.exceptions.ConnectionError:
        logger.info("⚠️  Ollama not running. Starting...")
        try:
            # Start Ollama in background
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            # Wait for startup
            for _ in range(10):
                try:
                    requests.get("http://localhost:11434", timeout=2)
                    logger.info("✅ Ollama started successfully")
                    break
                except:
                    time.sleep(1)
            else:
                logger.error("❌ Failed to start Ollama")
                return False
        except FileNotFoundError:
            logger.error("❌ Ollama executable not found. Please install Ollama.")
            return False

    # 2. Check Model
    model_name = "qwen2.5:7b" # Should match config
    try:
        # List models
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = [m['name'] for m in response.json().get('models', [])]
            # Check for exact match or with :latest tag
            if model_name not in models and f"{model_name}:latest" not in models and not any(m.startswith(model_name) for m in models):
                logger.info(f"⬇️  Pulling model {model_name}...")
                # Pull model (blocking)
                subprocess.run(["ollama", "pull", model_name], check=True)
                logger.info(f"✅ Model {model_name} ready")
            else:
                logger.info(f"✅ Model {model_name} available")
        return True
    except Exception as e:
        logger.error(f"❌ Error checking/pulling model: {e}")
        return False

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    init_llm_service()