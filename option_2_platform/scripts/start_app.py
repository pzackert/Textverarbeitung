#!/usr/bin/env python
import uvicorn
import os
import sys
from pathlib import Path

# Add project root to python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from init_system import init_llm_service

if __name__ == "__main__":
    print("🚀 IFB PROFI System-Start\n")
    
    # LLM initialisieren
    if not init_llm_service():
        print("\n⚠️  LLM-Service nicht verfügbar")
        # response = input("Trotzdem fortfahren? (j/n): ")
        # if response.lower() != 'j':
        #    return
        print("Fahre fort ohne LLM...")
    
    print("\n🌐 Starte Webserver...\n")
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
