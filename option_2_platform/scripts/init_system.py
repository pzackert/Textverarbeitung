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

def check_ollama():
    """Check if Ollama is running and model is available."""
    try:
        # Check service
        response = requests.get("http://localhost:11434", timeout=2)
        if response.status_code == 200:
            logger.info("✅ Ollama Service: Running")
        else:
            logger.warning("⚠️  Ollama Service: Running but returned unexpected status")
            
        # Check model
        config = load_config()
        model_name = config.llm.model
        
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            found = False
            for m in models:
                if model_name in m.get("name", ""):
                    found = True
                    size_gb = m.get("size", 0) / (1024**3)
                    logger.info(f"✅ Model {model_name}: Loaded ({size_gb:.1f}GB)")
                    break
            
            if not found:
                logger.warning(f"⚠️  Model {model_name}: Not found in Ollama")
                logger.info(f"   → Run: ollama pull {model_name}")
    except requests.exceptions.ConnectionError:
        logger.error("❌ Ollama Service: Not Running")
        logger.info("   → Run: ollama serve")
    except Exception as e:
        logger.error(f"❌ Ollama Check Failed: {e}")

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
