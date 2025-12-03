from typing import List, Optional
from sentence_transformers import SentenceTransformer
import logging
from src.rag.exceptions import RAGException

logger = logging.getLogger(__name__)

class EmbeddingGenerator:
    """
    Generate embeddings for text chunks using sentence-transformers.
    Supports German language via multilingual models.
    """
    
    def __init__(self, model_name: str = "paraphrase-multilingual-MiniLM-L12-v2"):
        """
        Initialize with specific model.
        
        Args:
            model_name: Name of the sentence-transformers model to use.
        """
        self.model_name = model_name
        try:
            logger.info(f"Loading embedding model: {model_name}")
            self.model = SentenceTransformer(model_name)
            logger.info("Model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model {model_name}: {e}")
            raise RAGException(f"Failed to load embedding model: {e}")
            
    def embed(self, text: str) -> List[float]:
        """
        Generate embedding for single text.
        
        Args:
            text: The text to embed.
            
        Returns:
            List[float]: The embedding vector.
        """
        if not text or not isinstance(text, str):
            logger.warning("Empty or invalid text provided for embedding")
            return []
            
        try:
            # encode returns numpy array, convert to list
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise RAGException(f"Error generating embedding: {e}")
        
    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts (more efficient).
        
        Args:
            texts: List of texts to embed.
            
        Returns:
            List[List[float]]: List of embedding vectors.
        """
        if not texts:
            return []
            
        try:
            # encode returns numpy array of arrays
            embeddings = self.model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error generating batch embeddings: {e}")
            raise RAGException(f"Error generating batch embeddings: {e}")
        
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
