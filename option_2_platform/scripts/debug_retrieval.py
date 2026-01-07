
import chromadb
from sentence_transformers import SentenceTransformer

# Config
PERSIST_DIR = "data/chromadb"
COLLECTION_NAME = "ifb_documents"
MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def debug_retrieval():
    print("Loading Model...")
    model = SentenceTransformer(MODEL_NAME)
    
    print("Connecting to Chroma...")
    client = chromadb.PersistentClient(path=PERSIST_DIR)
    coll = client.get_collection(COLLECTION_NAME)
    
    query_text = "Wer bist du?"
    print(f"Embedding query: '{query_text}'")
    query_vec = model.encode([query_text]).tolist()
    
    print("Querying Chroma...")
    results = coll.query(
        query_embeddings=query_vec,
        n_results=10,
        where={"type": "global_knowledge"},
        include=["documents", "metadatas", "distances"]
    )
    
    print("--- Results ---")
    ids = results["ids"][0]
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    dists = results["distances"][0]
    
    for i in range(len(ids)):
        print(f"[{i}] Distance: {dists[i]:.4f}")
        print(f"    Doc: {metas[i].get('doc_name')} (ID: {ids[i]})")
        print(f"    Content: {docs[i][:100]}...")
        if "Herbert" in docs[i]:
            print("    *** THIS IS HERBERT ***")

if __name__ == "__main__":
    debug_retrieval()
