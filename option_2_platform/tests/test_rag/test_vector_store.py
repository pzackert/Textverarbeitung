"""
Unit tests for VectorStore using ChromaDB.
"""
import pytest
import tempfile
import shutil
import sys
from pathlib import Path

# Ensure src is in path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.rag.vector_store import VectorStore
from src.rag.embeddings import EmbeddingGenerator
from src.rag.models import Chunk

@pytest.fixture
def temp_db_path():
    """Create temporary directory for test database."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def embedder():
    """Shared embedding generator for tests."""
    return EmbeddingGenerator("paraphrase-multilingual-MiniLM-L12-v2")

@pytest.fixture
def vector_store(temp_db_path, embedder):
    """Create fresh vector store for each test."""
    return VectorStore(
        collection_name="test_collection",
        persist_directory=temp_db_path,
        embedding_function=embedder
    )

@pytest.fixture
def sample_chunks():
    """Sample chunks for testing."""
    return [
        Chunk(
            content="Die IFB Hamburg fördert innovative Unternehmen.",
            metadata={"source": "doc1.pdf", "chunk_id": 0, "source_file": "doc1.pdf", "file_type": "pdf"}
        ),
        Chunk(
            content="Fördervoraussetzungen müssen erfüllt sein.",
            metadata={"source": "doc1.pdf", "chunk_id": 1, "source_file": "doc1.pdf", "file_type": "pdf"}
        ),
        Chunk(
            content="Python ist eine beliebte Programmiersprache.",
            metadata={"source": "doc2.pdf", "chunk_id": 0, "source_file": "doc2.pdf", "file_type": "pdf"}
        ),
    ]

def test_vector_store_initialization(vector_store):
    """Test that vector store initializes correctly."""
    # Verify collection exists (via stats)
    stats = vector_store.get_collection_stats()
    assert stats['count'] == 0
    assert stats['name'] == "test_collection"

def test_add_single_chunk(vector_store, sample_chunks):
    """Test adding a single chunk."""
    chunk = sample_chunks[0]
    ids = vector_store.add_chunks([chunk])
    
    assert len(ids) == 1
    assert ids[0] == "doc1.pdf_0"
    
    stats = vector_store.get_collection_stats()
    assert stats['count'] == 1

def test_add_multiple_chunks(vector_store, sample_chunks):
    """Test batch adding chunks."""
    ids = vector_store.add_chunks(sample_chunks)
    
    assert len(ids) == 3
    assert "doc1.pdf_0" in ids
    assert "doc1.pdf_1" in ids
    assert "doc2.pdf_0" in ids
    
    stats = vector_store.get_collection_stats()
    assert stats['count'] == 3

def test_query_returns_results(vector_store, sample_chunks):
    """Test that queries return relevant results."""
    vector_store.add_chunks(sample_chunks)
    
    # Query: "IFB Förderung"
    results = vector_store.query("IFB Förderung", top_k=2)
    
    assert len(results) > 0
    # Top result should be about IFB
    assert "IFB" in results[0]['content']
    assert results[0]['score'] > 0.0

def test_german_text_query(vector_store, sample_chunks):
    """Test queries with German text and umlauts."""
    vector_store.add_chunks(sample_chunks)
    
    # Query with umlauts: "Fördervoraussetzungen"
    results = vector_store.query("Fördervoraussetzungen", top_k=1)
    
    assert len(results) == 1
    assert "Fördervoraussetzungen" in results[0]['content']

def test_metadata_filtering(vector_store, sample_chunks):
    """Test filtering by metadata."""
    vector_store.add_chunks(sample_chunks)
    
    # Query with filter: source="doc1.pdf"
    # Note: In sample_chunks, metadata key is "source"
    results = vector_store.query(
        "Unternehmen", 
        top_k=5, 
        metadata_filter={"source": "doc1.pdf"}
    )
    
    assert len(results) > 0
    for res in results:
        assert res['metadata']['source'] == "doc1.pdf"
        
    # Verify doc2 is NOT in results
    doc2_ids = [r['id'] for r in results if "doc2" in r['id']]
    assert len(doc2_ids) == 0

def test_persistence(temp_db_path, embedder, sample_chunks):
    """Test that data persists across sessions."""
    # Create store, add chunks, close (by letting variable go out of scope/recreating)
    store1 = VectorStore(
        collection_name="persist_test",
        persist_directory=temp_db_path,
        embedding_function=embedder
    )
    store1.add_chunks(sample_chunks)
    stats1 = store1.get_collection_stats()
    
    # Create new store instance (simulate restart)
    store2 = VectorStore(
        collection_name="persist_test",
        persist_directory=temp_db_path,
        embedding_function=embedder
    )
    stats2 = store2.get_collection_stats()
    
    # Verify data persisted
    assert stats1['count'] == stats2['count']
    assert stats2['count'] == 3

def test_collection_stats(vector_store, sample_chunks):
    """Test collection statistics."""
    # Initially empty
    stats = vector_store.get_collection_stats()
    assert stats['count'] == 0
    
    # After adding
    vector_store.add_chunks(sample_chunks)
    stats = vector_store.get_collection_stats()
    assert stats['count'] == len(sample_chunks)
