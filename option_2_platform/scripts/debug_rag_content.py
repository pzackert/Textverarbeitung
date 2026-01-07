
import sys
import chromadb
from pathlib import Path

# Config
PERSIST_DIR = "data/chromadb"
COLLECTION_NAME = "ifb_documents"

def debug_chroma():
    print(f"Opening ChromaDB at {PERSIST_DIR}...")
    try:
        client = chromadb.PersistentClient(path=PERSIST_DIR)
        coll = client.get_collection(COLLECTION_NAME)
    except Exception as e:
        print(f"[ERROR] Could not open collection: {e}")
        return

    count = coll.count()
    print(f"Total Chunks in Collection: {count}")
    
    # Query all global knowledge
    # Note: Chunks might be many, let's peek at them
    result = coll.get(where={"type": "global_knowledge"}, include=["metadatas", "documents"])
    
    ids = result["ids"]
    metadatas = result["metadatas"]
    documents = result["documents"]
    
    print(f"Global Knowledge Chunks Found: {len(ids)}")
    
    if len(ids) == 0:
        print("[FAIL] No Global Knowledge chunks found! Ingestion failed or Metadata is wrong.")
        # Check if there are ANY chunks and what their metadata is
        peek = coll.peek(limit=5)
        print("Peek at random 5 chunks:")
        for idx, m in enumerate(peek["metadatas"]):
            print(f"  - Meta: {m}")
    else:
        print("--- Content Dump ---")
        for i, doc in enumerate(documents):
            meta = metadatas[i]
            print(f"[{i}] Source: {meta.get('source')} | Doc: {meta.get('document')}")
            print(f"    Content Preview: {doc[:100]}...")
            if "Herbert" in doc:
                print("    [MATCH] Contains 'Herbert'")
            else:
                print("    [NO MATCH] 'Herbert' missing")
                
            if "Wer bist du" in doc:
                 print("    [MATCH] Contains 'Wer bist du'")

if __name__ == "__main__":
    debug_chroma()
