class RAGException(Exception):
    """Base exception for RAG system."""
    pass

class ChunkingError(RAGException):
    """Error during text splitting."""
    pass

class EmbeddingError(RAGException):
    """Error during embedding generation."""
    pass

class VectorStoreError(RAGException):
    """Error during vector store operations."""
    pass

class RetrievalError(RAGException):
    """Error during document retrieval."""
    pass

class LLMError(RAGException):
    """Error during LLM interaction."""
    pass
