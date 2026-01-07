import logging
from functools import lru_cache
from src.rag.config import RAGConfig
from src.rag.ingestion import IngestionPipeline
from src.rag.llm_chain import LLMChain
from src.rag.retrieval import RetrievalEngine
from src.rag.llm_provider import BaseLLMProvider, OllamaProvider
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
_vector_store: VectorStore | None = None
_embedding_generator: EmbeddingGenerator | None = None

def get_embedding_generator() -> EmbeddingGenerator:
    """Returns singleton EmbeddingGenerator."""
    global _embedding_generator
    if _embedding_generator is None:
        try:
            config = get_config()
            _embedding_generator = EmbeddingGenerator(model_name=config.embedding_model)
            logger.info("EmbeddingGenerator initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize EmbeddingGenerator: {e}")
            raise
    return _embedding_generator

def get_vector_store() -> VectorStore:
    """Returns singleton VectorStore using shared Embedder."""
    global _vector_store
    if _vector_store is None:
        try:
            config = get_config()
            embedder = get_embedding_generator()
            _vector_store = VectorStore(
                collection_name=config.collection_name,
                persist_directory=config.persist_directory,
                embedding_function=embedder
            )
            # Ensure schema compatibility
            _vector_store.ensure_schema(config.metadata_schema_version)
            logger.info("VectorStore initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize VectorStore: {e}")
            raise
    return _vector_store

def get_ingestion_pipeline() -> IngestionPipeline:
    """
    Returns a singleton instance of IngestionPipeline using shared VectorStore.
    """
    global _ingestion_pipeline
    if _ingestion_pipeline is None:
        try:
            config = get_config()
            vector_store = get_vector_store() # Inject shared store
            _ingestion_pipeline = IngestionPipeline(config, vector_store=vector_store)
            logger.info("IngestionPipeline initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize IngestionPipeline: {e}")
            raise
    return _ingestion_pipeline

def _build_llm_provider(config: RAGConfig) -> BaseLLMProvider:
    provider_name = (config.llm.provider or "ollama").lower()
    if provider_name in ("ollama", "lm_studio"):
        return OllamaProvider(
            model_name=config.llm.model,
            base_url=config.llm.base_url,
        )
    raise ValueError(f"Unsupported LLM provider: {provider_name}")


def get_llm_chain() -> LLMChain:
    """
    Returns a singleton instance of LLMChain using shared VectorStore.
    """
    global _llm_chain
    if _llm_chain is None:
        try:
            config = get_config()
            
            # Reuse shared VectorStore
            vector_store = get_vector_store()
            
            retrieval_engine = RetrievalEngine(
                vector_store=vector_store,
                config=config
            )
            
            llm_provider = _build_llm_provider(config)
            
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
            # Return a Mock Chain that handles queries gracefully
            class MockLLMChain:
                config = type('Config', (), {'llm_model': 'Error'})()
                llm_provider = type('Provider', (), {'model_name': 'Error', 'is_available': lambda: False})()
                def query(self, *args, **kwargs):
                    return {
                        "answer": f"System Error: LLM Service Unavailable. ({str(e)})",
                        "citations": [],
                        "sources": [],
                        "metadata": {"error": str(e)}
                    }
            _llm_chain = MockLLMChain()
            
    return _llm_chain
