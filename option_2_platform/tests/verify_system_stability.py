
import sys
import os
import requests
import time
from pathlib import Path
from typing import Dict, Any

# Add project root to path
sys.path.append(os.getcwd())

from src.rag.config import RAGConfig
from src.rag.vector_store import VectorStore
from src.rag.llm_chain import create_llm_chain

def check_backend_health(base_url: str = "http://localhost:8000"):
    print(f"[*] Checking Backend Health at {base_url}...")
    try:
        # 1. Root / Dashboard check
        r = requests.get(f"{base_url}/")
        if r.status_code == 200:
            print("  [OK] Dashboard accessible (200)")
        else:
            print(f"  [FAIL] Dashboard returned {r.status_code}")
            return False

        # 2. System Status
        r = requests.get(f"{base_url}/api/system/status")
        if r.status_code == 200:
            data = r.json()
            status = data.get("status")
            print(f"  [OK] System Status API: {status}")
        else:
            print(f"  [FAIL] System Status API returned {r.status_code}")
            return False

        # 3. Global Chat List (DB Check)
        r = requests.get(f"{base_url}/api/chats/global/list")
        if r.status_code == 200:
            print("  [OK] Global Chat List accessible")
        else:
            print(f"  [FAIL] Global Chat List returned {r.status_code}")
            return False
            
        return True
    except requests.exceptions.ConnectionError:
        print("  [CRITICAL] Would not connect to Backend. Is Uvicorn running?")
        return False

def check_rag_resilience():
    print("\n[*] Checking RAG Chain Resilience (Internal Logic)...")
    try:
        # Load Config
        config = RAGConfig.from_yaml()
        
        # Initialize Chain (this checks DB connection, LLM connection)
        print("  ... Initializing LLMChain (Real components)...")
        chain = create_llm_chain()
        
        # Test Query with empty/minimal DB
        print("  ... Executing Test Query 'Wer bist du?'...")
        try:
            result = chain.query("Wer bist du?")
            answer = result.get("answer", "")
            print(f"  [OK] Query successful. Answer length: {len(answer)}")
            if "error" in answer.lower() or "500" in answer:
                 print("  [WARN] Answer contains error keywords.")
        except Exception as e:
            print(f"  [FAIL] Query crashed: {e}")
            return False

        return True
    except Exception as e:
        print(f"  [FAIL] RAG Initialization failed: {e}")
        return False

def check_directories():
    print("\n[*] Checking Critical Directories...")
    dirs = [
        "data/chromadb",
        "data/global_knowledge",
        "logs"
    ]
    all_ok = True
    for d in dirs:
        if Path(d).exists():
            print(f"  [OK] Exists: {d}")
        else:
            print(f"  [WARN] Missing: {d}")
            # Not critical failing, but warning
    return all_ok

def main():
    print("=== IFB Platform Stability Check ===\n")
    
    dirs_ok = check_directories()
    rag_ok = check_rag_resilience()
    backend_ok = check_backend_health()
    
    print("\n=== SUMMARY ===")
    print(f"Directories: {'OK' if dirs_ok else 'WARN'}")
    print(f"RAG Logic:   {'OK' if rag_ok else 'FAIL'}")
    print(f"Backend API: {'OK' if backend_ok else 'FAIL'}")
    
    if rag_ok and backend_ok:
        print("\n[SUCCESS] System appears stable.")
        sys.exit(0)
    else:
        print("\n[FAILURE] System stability issues detected.")
        sys.exit(1)

if __name__ == "__main__":
    main()
