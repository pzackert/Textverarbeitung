#!/usr/bin/env python3
"""
System Initialization Script for IFB PROFI Platform.
Checks environment, dependencies, and services before startup.
"""
import sys
import os
import logging
import requests
from pathlib import Path
import shutil

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.core.config import load_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s"
)
logger = logging.getLogger("init_system")

def check_directories():
    """Ensure necessary directories exist."""
    dirs = [
        "data/chromadb",
        "data/input",
        "data/samples",
        "logs",
        "frontend/static"
    ]
    
    created = []
    for d in dirs:
        path = Path(d)
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
            created.append(d)
            
    if created:
        logger.info(f"✅ Created directories: {', '.join(created)}")
    else:
        logger.info("✅ Directories: OK")

import subprocess
import time

# ...existing code...

def check_and_start_ollama():
    """Check if Ollama is running, if not: provide instructions or auto-start."""
    try:
        requests.get("http://localhost:11434", timeout=2)
        return True
    except requests.exceptions.ConnectionError:
        # Try to auto-start
        try:
            logger.info("🔄 Attempting to auto-start Ollama...")
            subprocess.Popen(["ollama", "serve"], 
                             stdout=subprocess.DEVNULL,
                             stderr=subprocess.DEVNULL)
            
            # Wait for startup
            for _ in range(10):
                time.sleep(1)
                try:
                    requests.get("http://localhost:11434", timeout=2)
                    logger.info("✅ Ollama auto-started successfully")
                    return True
                except:
                    continue
        except FileNotFoundError:
            logger.error("❌ Ollama executable not found")
        except Exception as e:
            logger.error(f"❌ Auto-start failed: {e}")
            
        logger.error("❌ Ollama Service: Not Running")
        logger.info("   → Run: ollama serve")
        return False

def ensure_model_loaded(model_name: str):
    """Ensure model is pulled and ready."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            for m in models:
                if model_name in m.get("name", ""):
                    size_gb = m.get("size", 0) / (1024**3)
                    logger.info(f"✅ Model {model_name}: Loaded ({size_gb:.1f}GB)")
                    return True
            
            # Not found, try to pull
            logger.info(f"🔄 Pulling model {model_name} (this may take a while)...")
            subprocess.run(["ollama", "pull", model_name], check=True)
            logger.info(f"✅ Model {model_name} pulled successfully")
            return True
    except Exception as e:
        logger.error(f"❌ Model Check Failed: {e}")
        return False

def check_ollama():
    """Check if Ollama is running and model is available."""
    if check_and_start_ollama():
        config = load_config()
        model_name = config.get("llm", {}).get("model", "qwen2.5:7b")
        ensure_model_loaded(model_name)

def check_chromadb():
    """Check if ChromaDB persistence directory is accessible."""
    try:
        db_path = Path("data/chromadb")
        if db_path.exists() and os.access(db_path, os.W_OK):
            logger.info("✅ ChromaDB: Storage accessible")
        else:
            logger.warning("⚠️  ChromaDB: Storage path might not be writable")
    except Exception as e:
        logger.error(f"❌ ChromaDB Check Failed: {e}")

def main():
    print("\n🔍 System Initialization Check")
    print("============================")
    
    check_directories()
    check_ollama()
    check_chromadb()
    
    print("\n🟢 System Ready (or warnings above)\n")

if __name__ == "__main__":
    main()
