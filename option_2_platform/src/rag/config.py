from pydantic import BaseModel
from src.core.config import load_config

class RAGConfig(BaseModel):
    """
    Configuration model for the RAG system.
    """
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "paraphrase-multilingual-MiniLM-L12-v2"
    top_k: int = 5
    similarity_threshold: float = 0.7
    persist_directory: str = "data/chromadb"
    collection_name: str = "ifb_documents"
    vector_store_path: str = "data/chromadb"

    # LLM Settings
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:7b"
    llm_base_url: str = "http://localhost:11434"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000

    # Prompt Settings
    default_template: str = "standard"
    include_scores: bool = False
    max_context_chunks: int = 5

    @classmethod
    def from_yaml(cls) -> "RAGConfig":
        """
        Loads RAG configuration from the central config.yaml file.
        """
        config_data = load_config().get("rag", {})
        return cls(**config_data)
