import logging
from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas import SystemStatus, LLMServiceStatus, LLMModelStatus, VectorDBStatus
from src.api.dependencies import get_config, get_llm_chain
from src.rag.config import RAGConfig
from src.rag.llm_chain import LLMChain

router = APIRouter(prefix="/system", tags=["system"])
logger = logging.getLogger(__name__)

@router.get("/health", response_model=SystemStatus)
async def health_check(
    llm_chain: LLMChain = Depends(get_llm_chain),
    config: RAGConfig = Depends(get_config)
):
    """
    Check the health of the system components (Ollama, ChromaDB).
    """
    logger.info("Health check performed")
    
    # Check Ollama
    ollama_available = llm_chain.llm_provider.is_available()
    model_info = llm_chain.llm_provider.get_model_info()
    
    # Check ChromaDB via VectorStore
    try:
        # Accessing the underlying collection count to verify connection
        doc_count = llm_chain.retrieval_engine.vector_store.collection.count()
        chromadb_available = True
    except Exception as e:
        logger.error(f"ChromaDB check failed: {e}")
        chromadb_available = False
        doc_count = 0
        
    # Check embedding cache (if available)
    embeddings_cached = 0
    if hasattr(llm_chain.retrieval_engine.vector_store.embedding_function, "_cache"):
         embeddings_cached = len(llm_chain.retrieval_engine.vector_store.embedding_function._cache or {})

    return SystemStatus(
        llm_service=LLMServiceStatus(
            available=ollama_available,
            provider="ollama",
            base_url=llm_chain.llm_provider.base_url,
            can_autostart=not ollama_available,
            instructions="Run: ollama serve" if not ollama_available else None
        ),
        llm_model=LLMModelStatus(
            loaded=model_info["loaded"],
            name=model_info["name"],
            size=model_info["size"],
            can_autopull=not model_info["loaded"],
            instructions=f"Run: ollama pull {model_info['name']}" if not model_info["loaded"] else None
        ),
        vector_db=VectorDBStatus(
            available=chromadb_available,
            documents=doc_count
        ),
        # Backward compatibility
        ollama_available=ollama_available,
        chromadb_available=chromadb_available,
        documents_count=doc_count,
        embeddings_cached=embeddings_cached
    )

@router.get("/config")
async def get_current_config(config: RAGConfig = Depends(get_config)):
    """
    Get the current RAG configuration.
    """
    logger.info("Config requested")
    return config.dict()

@router.get("/stats")
async def get_stats(llm_chain: LLMChain = Depends(get_llm_chain)):
    """
    Get system statistics.
    """
    logger.info("Stats requested")
    
    doc_count = llm_chain.retrieval_engine.vector_store.collection.count()
    
    return {
        "documents_count": doc_count,
        "collection_name": llm_chain.retrieval_engine.vector_store.collection_name,
        "persist_directory": llm_chain.retrieval_engine.vector_store.persist_directory
    }
