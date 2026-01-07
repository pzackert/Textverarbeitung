import requests
import json
import logging

logging.basicConfig(level=logging.INFO)

# 1. LLM Payload (Verified OK)
llm_payload = {
    "provider": "ollama",
    "model": "qwen2.5:7b",
    "temperature": 0.5,
    "max_tokens": 1000,
    "timeout": 60,
    "lm_studio": {},
    "ollama": {}
}

# 2. RAG Payload
# config.rag in settings.html: { chunk_size: ..., chunk_overlap: ..., top_k: ... }
# Frontend likely merges whatever is in api response.
# Config.yaml has: embedding_model, persist_directory, etc.
rag_payload = {
    "chunk_size": 1000,
    "chunk_overlap": 50,
    "top_k": 10,
    # Extra fields causing 422?
    "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
    "persist_directory": "data/chromadb",
    "collection_name": "ifb_documents"
}

# 3. Prompts Payload
prompts_payload = {
    "begruessung": "Final Test Value",
    "global_chat_initial": "Prompt A",
    "antrags_chat_initial": "Prompt B",
    "antwort_richtlinie": "Prompt C",
    "kriterien_pruefung": "Prompt D"
    # Frontend usually doesn't have extra fields here unless I added something?
}

def test_endpoint(name, url, payload):
    print(f"\n--- Testing {name} ({url}) ---")
    try:
        resp = requests.post(url, json=payload)
        print(f"Status: {resp.status_code}")
        if not resp.ok:
            print(f"Error: {resp.text}")
        else:
            print("OK")
    except Exception as e:
        print(f"Exception: {e}")

test_endpoint("LLM", "http://127.0.0.1:8000/api/settings/llm", llm_payload)
test_endpoint("RAG", "http://127.0.0.1:8000/api/settings/rag", rag_payload)
test_endpoint("Prompts", "http://127.0.0.1:8000/api/settings/prompts", prompts_payload)
