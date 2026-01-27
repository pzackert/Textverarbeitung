import sys
import os
from pathlib import Path
import logging

# Add src to path
sys.path.append(os.getcwd())

from src.rag.vector_store import VectorStore
from src.rag.models import Chunk
from src.rag.config import RAGConfig
from src.rag.retrieval import RetrievalEngine

# Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_rag_logic():
    print("--- Starting RAG Logic Verification ---")
    
    # 1. Setup Vector Store (InMemory or Test Collection)
    # We use a unique collection name to avoid messing with real data
    test_collection = "verify_backend_test"
    
    # Mock Config
    config = RAGConfig.from_yaml()
    config.collection_name = test_collection
    config.similarity_threshold = 0.5 # Test threshold
    
    # Initialize implementation
    # Note: We need a dummy embedding function or real one. 
    # Real one is better to check Chroma behavior.
    from src.rag.embeddings import EmbeddingGenerator
    embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2") 
    
    vs = VectorStore(
        collection_name=test_collection,
        persist_directory="data/chromadb_test",
        embedding_function=embedder
    )
    vs.clear_collection()
    
    # 2. Add Test Data
    print("Adding Test Chunks...")
    
    # Global Chunk (Herbert)
    chunk_global = Chunk(
        content="Ich bin Herbert, der Sachbearbeiter.",
        metadata={"type": "global_knowledge", "document": "herbert.txt", "doc_id": "g1"},
        embedding=embedder.embed("Ich bin Herbert, der Sachbearbeiter.")
    )
    
    # Project A Chunk
    chunk_a = Chunk(
        content="Das Projekt A handelt von Solarzellen.",
        metadata={"project_id": "PROJ_A", "doc_name": "solar.pdf", "doc_id": "a1"},
        embedding=embedder.embed("Das Projekt A handelt von Solarzellen.")
    )
    
    # Project B Chunk
    chunk_b = Chunk(
        content="Das Projekt B handelt von Windkraft.",
        metadata={"project_id": "PROJ_B", "doc_name": "wind.pdf", "doc_id": "b1"},
        embedding=embedder.embed("Das Projekt B handelt von Windkraft.")
    )
    
    vs.add_chunks([chunk_global, chunk_a, chunk_b])
    
    # 3. Test Isolation (Fix 2.1)
    print("\nTest 1: Project Isolation (PROJ_A Context)")
    # Filter: Project A OR Global
    filter_a = {
        "$or": [
            {"project_id": {"$eq": "PROJ_A"}},
            {"type": {"$eq": "global_knowledge"}}
        ]
    }
    
    results_a = vs.query(
        query_text="Worum geht es in den Projekten und wer bist du?",
        top_k=10,
        metadata_filter=filter_a
    )
    
    found_ids = [r['metadata'].get('doc_id') for r in results_a]
    print(f"Propagated IDs: {found_ids}")
    
    assert "g1" in found_ids, "Global Knowledge (Herbert) missing in Project A context!"
    assert "a1" in found_ids, "Project A Knowledge (Solar) missing in Project A context!"
    assert "b1" not in found_ids, "Project B Knowledge (Wind) LEAKED into Project A context!"
    print("-> SUCCESS: Logic correctly isolates A and includes Global.")
    
    # 4. Test Threshold (Fix 2.3)
    print("\nTest 2: Similarity Threshold")
    # Query completely irrelevant
    retrieval = RetrievalEngine(vector_store=vs, config=config)
    # config.similarity_threshold is 0.5.
    
    # Query: "Herbert" -> Should match g1 (high score).
    # Query: "Kuchen backen" -> Should retrieval low score.
    
    res_relevant = retrieval.retrieve("Herbert", top_k=5)
    print(f"Relevant Query Count: {len(res_relevant)}")
    assert len(res_relevant) > 0
    
    res_irrelevant = retrieval.retrieve("Xylophon Quantenmechanik Rezept", top_k=5)
    # This might still match something if vector space is small, but score should be low.
    # We check if filtering happens.
    
    print("Checking scores...")
    for r in res_irrelevant:
        print(f"Irrelevant Result Score: {r.get('score')}")
    
    # Note: If embedding model is robust, score should be low.
    # User complained about "10 sources" often being garbage.
    # Our fix in retrieval.py filters by threshold.
    # If all scores < 0.5, result count should be 0.
    
    if len(res_irrelevant) == 0:
        print("-> SUCCESS: Irrelevant results filtered out completely.")
    else:
        print(f"-> PARTIAL: {len(res_irrelevant)} results remained. Checking scores against threshold.")
        for r in res_irrelevant:
            assert r['score'] >= (1.0 - 0.5), f"Result score {r['score']} is below threshold but was returned!"
            
    print("\n--- Verification Completed Successfully ---")

if __name__ == "__main__":
    test_rag_logic()
