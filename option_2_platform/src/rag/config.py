from pydantic import BaseModel
from src.core.config import load_config

class RAGConfig(BaseModel):
    """
    Configuration model for the RAG system.
    """
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    top_k: int = 5
    similarity_threshold: float = 0.7
    persist_directory: str = "data/chromadb"
    collection_name: str = "ifb_documents"

    @classmethod
    def from_yaml(cls) -> "RAGConfig":
        """
        Loads RAG configuration from the central config.yaml file.
        """
        config_data = load_config().get("rag", {})
        return cls(**config_data)
