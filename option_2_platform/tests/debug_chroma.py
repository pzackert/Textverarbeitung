
import chromadb
from chromadb.config import Settings
import logging

def check_chroma():
    persist_dir = "data/chromadb"
    collection_name = "ifb_documents"
    
    print(f"Checking ChromaDB at {persist_dir}...")
    client = chromadb.PersistentClient(path=persist_dir)
    
    try:
        coll = client.get_collection(collection_name)
    except Exception as e:
        print(f"Collection not found: {e}")
        return

    print(f"Collection count: {coll.count()}")
    
    # Peek at all items (up to 100)
    data = coll.get(include=["metadatas", "documents"])
    ids = data["ids"]
    metadatas = data["metadatas"]
    documents = data["documents"]
    
    found_herbert = False
    for i, meta in enumerate(metadatas):
        doc_name = meta.get("doc_name") or meta.get("document") or meta.get("source")
        if doc_name and ("herbert" in doc_name.lower()):
            print("FOUND HERBERT CHUNK:")
            print(f"ID: {ids[i]}")
            print(f"Metadata: {meta}")
            print(f"Content: {documents[i][:50]}...")
            found_herbert = True
            
    if not found_herbert:
        print("❌ Herbert NOT found in collection.")
    else:
        print("✅ Herbert found.")

if __name__ == "__main__":
    check_chroma()
