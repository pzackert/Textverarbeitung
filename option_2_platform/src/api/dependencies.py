import logging
from functools import lru_cache
from src.rag.config import RAGConfig
from src.rag.ingestion import IngestionPipeline
from src.rag.llm_chain import LLMChain
from src.rag.retrieval import RetrievalEngine
from src.rag.llm_provider import OllamaProvider
from src.rag.prompt_builder import PromptBuilder
from src.rag.vector_store import VectorStore
from src.rag.embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

@lru_cache()
def get_config() -> RAGConfig:
    """
    Returns a cached instance of RAGConfig.
    """
    try:
        # In a real scenario, we might load from a file here
        # For now, we use the default or environment variables
        config = RAGConfig.from_yaml() # Use from_yaml to load defaults/file
        logger.info("RAGConfig loaded successfully.")
        return config
    except Exception as e:
        logger.error(f"Failed to load RAGConfig: {e}")
        raise

# Global instances to act as singletons
_ingestion_pipeline: IngestionPipeline | None = None
_llm_chain: LLMChain | None = None

def get_ingestion_pipeline() -> IngestionPipeline:
    """
    Returns a singleton instance of IngestionPipeline.
    """
    global _ingestion_pipeline
    if _ingestion_pipeline is None:
        try:
            config = get_config()
            _ingestion_pipeline = IngestionPipeline(config)
            logger.info("IngestionPipeline initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize IngestionPipeline: {e}")
            raise
    return _ingestion_pipeline

def get_llm_chain() -> LLMChain:
    """
    Returns a singleton instance of LLMChain.
    """
    global _llm_chain
    if _llm_chain is None:
        try:
            config = get_config()
            
            # Initialize dependencies
            embedding_generator = EmbeddingGenerator(model_name=config.embedding_model)
            
            vector_store = VectorStore(
                collection_name=config.collection_name,
                persist_directory=config.persist_directory,
                embedding_function=embedding_generator
            )
            
            retrieval_engine = RetrievalEngine(
                vector_store=vector_store,
                config=config
            )
            
            llm_provider = OllamaProvider(
                model_name=config.llm_model,
                base_url=config.llm_base_url
            )
            
            prompt_builder = PromptBuilder(retrieval_engine=retrieval_engine)
            
            _llm_chain = LLMChain(
                retrieval_engine=retrieval_engine,
                llm_provider=llm_provider,
                prompt_builder=prompt_builder,
                config=config
            )
            logger.info("LLMChain initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize LLMChain: {e}")
            raise
    return _llm_chain
