import logging
from fastapi import APIRouter, Depends, HTTPException
from src.api.schemas import SystemStatus
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
    
    ollama_status = llm_chain.llm_provider.is_available()
    
    # Check ChromaDB via VectorStore
    try:
        # Accessing the underlying collection count to verify connection
        doc_count = llm_chain.retrieval_engine.vector_store.collection.count()
        chromadb_status = True
    except Exception as e:
        logger.error(f"ChromaDB check failed: {e}")
        chromadb_status = False
        doc_count = 0
        
    # Check embedding cache (if available)
    embeddings_cached = 0
    if hasattr(llm_chain.retrieval_engine.vector_store.embedding_function, "_cache"):
         embeddings_cached = len(llm_chain.retrieval_engine.vector_store.embedding_function._cache or {})

    return SystemStatus(
        ollama_available=ollama_status,
        chromadb_available=chromadb_status,
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
