import pytest
import numpy as np
import time
from typing import List
from src.rag.embeddings import EmbeddingGenerator
from src.rag.exceptions import RAGException

# Helper function for cosine similarity
def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

@pytest.fixture(scope="module")
def embedder():
    """Fixture providing EmbeddingGenerator instance. Scoped to module to load model once."""
    return EmbeddingGenerator("paraphrase-multilingual-MiniLM-L12-v2")

@pytest.fixture
def sample_texts():
    """Fixture providing various test texts."""
    return {
        "german": "Die IFB Hamburg fördert Innovationsprojekte.",
        "german_umlauts": "Förderung für Unternehmen mit Umlauten: ä, ö, ü, ß",
        "english": "The bank supports innovation projects.",
        "similar_1": "Die IFB fördert innovative Unternehmen.",
        "similar_2": "Innovative Firmen werden von der IFB unterstützt.",
        "different": "Das Wetter ist heute schön.",
        "long": "Ein sehr langer Text... " * 100,
        "empty": "",
        "special": "!!!###$$$",
        "numbers": "123 456 789"
    }

class TestEmbeddingGenerator:
    """Test suite for EmbeddingGenerator class."""

    def test_model_loading(self, embedder):
        """Test that model loads successfully."""
        assert embedder is not None
        assert embedder.model_name == "paraphrase-multilingual-MiniLM-L12-v2"
        assert embedder.get_dimension() == 384

    def test_single_embedding(self, embedder, sample_texts):
        """Test embedding generation for single text."""
        text = sample_texts["german"]
        embedding = embedder.embed(text)
        
        assert isinstance(embedding, list)
        assert len(embedding) == 384
        assert all(isinstance(x, float) for x in embedding)
        
        # Check normalization (values roughly between -1 and 1)
        assert all(-1.5 <= x <= 1.5 for x in embedding)

    def test_batch_embedding(self, embedder, sample_texts):
        """Test batch embedding generation."""
        texts = [
            sample_texts["german"],
            sample_texts["english"],
            sample_texts["similar_1"]
        ]
        
        start_time = time.time()
        embeddings = embedder.embed_batch(texts)
        batch_time = time.time() - start_time
        
        assert isinstance(embeddings, list)
        assert len(embeddings) == 3
        assert all(len(emb) == 384 for emb in embeddings)
        
        # Compare with sequential processing (rough check)
        start_seq = time.time()
        for text in texts:
            embedder.embed(text)
        seq_time = time.time() - start_seq
        
        # Batch should generally be faster or comparable, but hard to assert strictly in CI/local
        # Just ensure it works correctly
        print(f"\nBatch time: {batch_time:.4f}s, Sequential time: {seq_time:.4f}s")

    def test_german_text_embedding(self, embedder, sample_texts):
        """Test embeddings for German text with special characters."""
        text = sample_texts["german_umlauts"]
        embedding = embedder.embed(text)
        
        assert len(embedding) == 384
        # Ensure it's not all zeros or NaNs
        assert not np.allclose(embedding, 0)
        assert not np.isnan(embedding).any()

    def test_semantic_similarity(self, embedder, sample_texts):
        """Test that similar texts have similar embeddings."""
        emb1 = embedder.embed(sample_texts["similar_1"])
        emb2 = embedder.embed(sample_texts["similar_2"])
        emb3 = embedder.embed(sample_texts["different"])
        
        sim_high = cosine_similarity(emb1, emb2)
        sim_low = cosine_similarity(emb1, emb3)
        
        print(f"\nSimilarity (High): {sim_high:.4f}")
        print(f"Similarity (Low): {sim_low:.4f}")
        
        assert sim_high > 0.7, f"Expected high similarity > 0.7, got {sim_high}"
        assert sim_low < 0.4, f"Expected low similarity < 0.4, got {sim_low}"
        assert sim_high > sim_low

    def test_edge_cases(self, embedder, sample_texts):
        """Test edge cases and error handling."""
        # Empty string
        empty_emb = embedder.embed(sample_texts["empty"])
        assert empty_emb == [] # Should return empty list for empty input
        
        # Special characters
        special_emb = embedder.embed(sample_texts["special"])
        assert len(special_emb) == 384
        
        # Numbers
        num_emb = embedder.embed(sample_texts["numbers"])
        assert len(num_emb) == 384
        
        # Long text
        long_emb = embedder.embed(sample_texts["long"])
        assert len(long_emb) == 384

    def test_embedding_consistency(self, embedder, sample_texts):
        """Test that same text produces same embedding."""
        text = sample_texts["german"]
        emb1 = embedder.embed(text)
        emb2 = embedder.embed(text)
        emb3 = embedder.embed(text)
        
        assert np.allclose(emb1, emb2)
        assert np.allclose(emb1, emb3)

    def test_get_dimension(self, embedder):
        """Test dimension getter method."""
        dim = embedder.get_dimension()
        assert isinstance(dim, int)
        assert dim == 384
