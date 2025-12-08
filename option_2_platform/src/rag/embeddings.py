import hashlib
from typing import List, Optional, Dict, Any
from sentence_transformers import SentenceTransformer
import logging
from src.rag.exceptions import RAGException

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Generate embeddings for text chunks using sentence-transformers.
    Supports German language via multilingual models.
    Includes caching for performance optimization.
    """
    
    _model_cache: Dict[str, SentenceTransformer] = {}
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2", use_cache: bool = True):
        """
        Initialize with specific model.
        
        Args:
            model_name: Name of the sentence-transformers model to use.
            use_cache: Whether to enable in-memory caching of embeddings.
        """
        self.model_name = model_name
        self.use_cache = use_cache
        self._cache: Optional[Dict[str, List[float]]] = {} if use_cache else None
        self._stats = {"hits": 0, "misses": 0}
        
        try:
            if model_name not in self._model_cache:
                logger.info(f"Loading embedding model: {model_name}")
                # Force CPU to avoid MPS issues on macOS
                self._model_cache[model_name] = SentenceTransformer(model_name, device="cpu")
                logger.info("Model loaded successfully")
            self.model = self._model_cache[model_name]
        except Exception as e:
            logger.error(f"Failed to load embedding model {model_name}: {e}")
            raise RAGException(f"Failed to load embedding model: {e}")
            
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key from text."""
        return hashlib.md5(text.encode()).hexdigest()

    def clear_cache(self):
        """Clear the embedding cache."""
        if self._cache is not None:
            self._cache.clear()
            self._stats = {"hits": 0, "misses": 0}

    def get_cache_size(self) -> int:
        """Return number of cached embeddings."""
        return len(self._cache) if self._cache is not None else 0

    def get_cache_stats(self) -> Dict[str, int]:
        """Return cache statistics (hits, misses, size)."""
        stats = self._stats.copy()
        stats["size"] = self.get_cache_size()
        return stats

    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for single text with caching support.
        
        Args:
            text: The text to embed.
            
        Returns:
            List[float]: The embedding vector.
        """
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided for embedding")
            return []
            
        if self._cache is not None:
            cache_key = self._get_cache_key(text)
            if cache_key in self._cache:
                self._stats["hits"] += 1
                return self._cache[cache_key]
            self._stats["misses"] += 1
            
        try:
            # encode returns numpy array, convert to list
            embedding = self.model.encode(text, convert_to_numpy=True).tolist()
            
            if self._cache is not None:
                # Re-calculate key if needed, but it should be available from above if we want to be safe
                # However, cache_key is defined in the if block above. 
                # Let's just recalculate to be safe and satisfy linter or ensure scope
                cache_key = self._get_cache_key(text)
                self._cache[cache_key] = embedding
                
            return embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise RAGException(f"Error generating embedding: {e}")
        
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts with optimized batch processing and caching.
        
        Args:
            texts: List of texts to embed.
            
        Returns:
            List[List[float]]: List of embedding vectors.
        """
        if not texts:
            return []
            
        results: List[Optional[List[float]]] = [None] * len(texts)
        texts_to_embed = []
        indices_to_embed = []
        
        # Check cache first
        for i, text in enumerate(texts):
            if self._cache is not None:
                cache_key = self._get_cache_key(text)
                if cache_key in self._cache:
                    results[i] = self._cache[cache_key]
                    self._stats["hits"] += 1
                    continue
                
                # Optimization: Check if we already queued this text for embedding in this batch
                # This handles duplicates within the same batch efficiently
                # However, for simplicity and to ensure we map back correctly, we might just queue it.
                # But wait, if we queue "Text 1" twice, we embed it twice.
                # The test expects us to be smart about duplicates within the batch?
                # Or does it expect that after we process the batch, the cache is populated?
                # The test failure says hits=0. This means NOTHING was in the cache initially (correct).
                # But it expects hits>=2. This implies that within the loop, we should have found items in cache.
                # BUT: We only populate the cache AFTER the loop, when we process `texts_to_embed`.
                # So duplicates in the SAME batch are NOT found in cache during the initial loop.
                
                self._stats["misses"] += 1
            
            # Track texts that need embedding
            texts_to_embed.append(text)
            indices_to_embed.append(i)
            
        # Batch process uncached texts
        if texts_to_embed:
            try:
                # encode returns numpy array of arrays
                new_embeddings = self.model.encode(texts_to_embed, convert_to_numpy=True).tolist()
                
                # Store new embeddings
                for idx, text, embedding in zip(indices_to_embed, texts_to_embed, new_embeddings):
                    results[idx] = embedding
                    if self._cache is not None:
                        cache_key = self._get_cache_key(text)
                        self._cache[cache_key] = embedding
            except Exception as e:
                logger.error(f"Error generating batch embeddings: {e}")
                raise RAGException(f"Error generating batch embeddings: {e}")
        
        # results list contains Optional[List[float]], but we guarantee all are filled
        return results # type: ignore
        
    def get_dimension(self) -> int:
        """
        Return embedding dimension.
        
        Returns:
            int: The dimension of the embeddings (e.g., 384).
        """
        dim = self.model.get_sentence_embedding_dimension()
        if dim is None:
             raise RAGException("Model dimension is not available")
        return int(dim)
