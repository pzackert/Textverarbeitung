"""Test: RAG System (Chunker + VectorStore)"""
import pytest
from backend.rag.chunker import chunk_text
from backend.rag.vector_store import VectorStore


def test_chunker():
    """Test Text Chunking"""
    text = "Dies ist ein Test. " * 100
    chunks = chunk_text(text, chunk_size=100, chunk_overlap=20)
    
    assert len(chunks) > 0
    assert all(len(c) <= 100 for c in chunks)


def test_vector_store():
    """Test VectorStore (ChromaDB + Embeddings)"""
    store = VectorStore()
    store.clear_all()
    
    # Index
    texts = ["Unternehmen in Thüringen", "Fördersumme 200000 Euro", "KMU Status"]
    metadatas = [{"doc": "test", "chunk": i} for i in range(len(texts))]
    ids = [f"test_{i}" for i in range(len(texts))]
    
    store.add_documents(texts, metadatas, ids)
    
    # Search
    results = store.search("Wo ist das Unternehmen?", top_k=2)
    
    assert len(results) == 2
    assert "distance" in results[0]
    assert "text" in results[0]


def test_rag_pipeline():
    """Test komplette RAG Pipeline"""
    text = "Das Unternehmen hat seinen Sitz in Erfurt, Thüringen. Die Fördersumme beträgt 150.000 Euro."
    
    # Chunk
    chunks = chunk_text(text, chunk_size=50, chunk_overlap=10)
    assert len(chunks) >= 2
    
    # Index
    store = VectorStore()
    store.clear_all()
    store.add_documents(
        chunks,
        [{"doc": "test", "chunk": i} for i in range(len(chunks))],
        [f"test_{i}" for i in range(len(chunks))]
    )
    
    # Retrieve
    results = store.search("Wo ist der Unternehmenssitz?", top_k=1)
    assert len(results) == 1
    assert "Thüringen" in results[0]["text"] or "Erfurt" in results[0]["text"]
