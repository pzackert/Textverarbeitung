import logging
import time
from typing import Dict, Any, Optional, List

from .config import RAGConfig
from .retrieval import RetrievalEngine
from .llm_provider import BaseLLMProvider, OllamaProvider
from .prompt_builder import PromptBuilder
from .response_parser import ResponseParser
from .vector_store import VectorStore
from .embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

class LLMChain:
    """
    Complete RAG chain: Retrieval -> Prompt -> LLM -> Response.
    """
    
    def __init__(
        self, 
        retrieval_engine: RetrievalEngine, 
        llm_provider: BaseLLMProvider, 
        prompt_builder: PromptBuilder, 
        config: RAGConfig
    ):
        """Initialize all components."""
        self.retrieval_engine = retrieval_engine
        self.llm_provider = llm_provider
        self.prompt_builder = prompt_builder
        self.config = config
        self.response_parser = ResponseParser()
        
    def query(
        self, 
        question: str, 
        template_type: str = "standard", 
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Execute complete RAG query.
        
        Args:
            question: User question
            template_type: Prompt template to use
            top_k: Number of chunks to retrieve (overrides config)
            
        Returns:
            Dict with answer, sources, citations, metadata
        """
        start_time = time.time()
        logger.info(f"Starting RAG query: {question[:50]}...")
        
        # 1. Retrieval
        logger.info("Step 1: Retrieving documents...")
        results = self.retrieval_engine.retrieve(
            query=question,
            top_k=top_k or self.config.top_k
        )
        
        if not results:
            logger.warning("No relevant documents found.")
            return {
                "answer": "Ich konnte leider keine relevanten Informationen in den Dokumenten finden.",
                "sources": [],
                "citations": [],
                "metadata": {"duration": time.time() - start_time}
            }
            
        # 2. Prompt Building
        logger.info(f"Step 2: Building prompt with {len(results)} chunks...")
        prompt = self.prompt_builder.build_query_prompt(
            query=question,
            template_type=template_type
        )
        
        # 3. LLM Generation
        logger.info("Step 3: Generating response from LLM...")
        try:
            response_text = self.llm_provider.generate(
                prompt=prompt,
                max_tokens=self.config.llm_max_tokens,
                temperature=self.config.llm_temperature
            )
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            raise
            
        # 4. Response Parsing
        logger.info("Step 4: Parsing response...")
        parsed_result = self.response_parser.parse(response_text, results)
        
        # 5. Result Assembly
        duration = time.time() - start_time
        parsed_result["metadata"] = {
            "duration": duration,
            "model": self.llm_provider.model_name,
            "chunks_retrieved": len(results)
        }
        
        logger.info(f"Query completed in {duration:.2f}s")
        return parsed_result

    def query_with_context(self, question: str) -> str:
        """Simple query returning just answer text."""
        result = self.query(question)
        return result["answer"]
    
    def query_detailed(self, question: str) -> Dict[str, Any]:
        """Detailed query with all metadata."""
        return self.query(question)

def create_llm_chain(config_path: str = "config/config.yaml") -> LLMChain:
    """
    Create complete LLM Chain from config.
    Initializes all components automatically.
    """
    logger.info("Initializing RAG Chain...")
    
    # 1. Load Config
    # Note: RAGConfig.from_yaml() loads from the standard location or we can pass path if modified
    # For now assuming standard loading logic in RAGConfig
    config = RAGConfig.from_yaml()
    
    # 2. Initialize Components
    embedding_generator = EmbeddingGenerator(model_name=config.embedding_model)
    
    vector_store = VectorStore(
        persist_directory=config.persist_directory,
        collection_name=config.collection_name,
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
    
    # Check LLM connection
    status = llm_provider.test_connection()
    if not status["available"]:
        logger.warning(f"LLM Provider not available: {status.get('error')}")
    else:
        logger.info(f"LLM Provider connected: {status.get('model_info')}")
        
    prompt_builder = PromptBuilder(retrieval_engine=retrieval_engine)
    
    # 3. Create Chain
    chain = LLMChain(
        retrieval_engine=retrieval_engine,
        llm_provider=llm_provider,
        prompt_builder=prompt_builder,
        config=config
    )
    
    logger.info("RAG Chain initialized successfully.")
    return chain
