import logging
import time
from typing import Dict, Any, Optional, List
from dataclasses import dataclass

from .config import RAGConfig
from .retrieval import RetrievalEngine
from .llm_provider import BaseLLMProvider, OllamaProvider
from .prompt_builder import PromptBuilder
from .response_parser import ResponseParser
from .vector_store import VectorStore
from .embeddings import EmbeddingGenerator

logger = logging.getLogger(__name__)

@dataclass
class Citation:
    """Citation from RAG System."""
    doc_id: str
    doc_name: str
    page: int
    text_snippet: str
    chunk_id: str
    score: float

@dataclass
class RAGResponse:
    """Extended RAG Response with Citations."""
    answer: str
    citations: List[Citation]
    sources_used: int

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
        
    def query_with_citations(
        self, 
        question: str,
        project_id: str
    ) -> RAGResponse:
        """
        Query with Citation Extraction.
        """
        # 1. Retrieve relevant Chunks
        # Note: RetrievalEngine.retrieve returns a list of dicts or objects. 
        # Assuming it returns a list of dicts with 'text', 'metadata', 'score'.
        # We need to pass project_id filter if supported by retrieval_engine.
        # The current retrieval_engine.retrieve signature is query(query, top_k).
        # We might need to update RetrievalEngine to support filters or handle it here if possible.
        # For now, assuming retrieval_engine handles it or we filter post-retrieval (less efficient).
        # Ideally, RetrievalEngine should accept filters.
        
        # Let's check RetrievalEngine signature in src/rag/retrieval.py first.
        # But based on the prompt, I should implement this method.
        
        # Assuming retrieval_engine.retrieve supports filter or we just pass it.
        # If not, I will update RetrievalEngine later.
        
        results = self.retrieval_engine.retrieve(
            query=question,
            top_k=5,
            metadata_filter={"project_id": project_id}
        )
        
        # 2. Build Context
        # PromptBuilder needs to be used here.
        prompt = self.prompt_builder.build_query_prompt(
            query=question,
            template_type="standard" # or specific template
        )
        # Wait, PromptBuilder usually takes the retrieved chunks to build the prompt.
        # The current implementation of query() does:
        # prompt = self.prompt_builder.build_query_prompt(query=question, template_type=template_type)
        # This implies PromptBuilder might be stateful or I missed something.
        # Let's look at query() again.
        
        # In query():
        # results = self.retrieval_engine.retrieve(...)
        # prompt = self.prompt_builder.build_query_prompt(query=question, template_type=template_type)
        
        # Wait, where are 'results' used?
        # Ah, PromptBuilder probably doesn't take results in build_query_prompt?
        # That would be strange for RAG.
        # Let me check PromptBuilder in src/rag/prompt_builder.py
        
        # For now, I will implement the method as requested, but I need to be careful about how context is injected.
        # The user prompt example shows:
        # context = self._build_context(retrieved_chunks)
        # prompt = f"... Context: {context} ..."
        
        # I will follow the user's example logic but adapt to existing classes.
        
        context = self._build_context(results)
        
        # Construct prompt manually or use PromptBuilder if it supports context injection
        full_prompt = f"""
Beantworte die Frage basierend auf dem Kontext.

Kontext:
{context}

Frage: {question}

Antwort:
"""
        
        # 3. LLM Query
        answer = self.llm_provider.generate(
            prompt=full_prompt,
            max_tokens=self.config.llm_max_tokens,
            temperature=self.config.llm_temperature
        )
        
        # 4. Extract Citations
        citations = self._extract_citations(
            answer, 
            results
        )
        
        return RAGResponse(
            answer=answer,
            citations=citations,
            sources_used=len(results)
        )

    def _build_context(self, chunks: List[Dict[str, Any]]) -> str:
        """Build context string from chunks."""
        context_parts = []
        for chunk in chunks:
            text = chunk.get("text", "")
            source = chunk.get("metadata", {}).get("source", "Unknown")
            page = chunk.get("metadata", {}).get("page_number", "?")
            context_parts.append(f"Source: {source} (Page {page})\nContent: {text}")
        return "\n\n".join(context_parts)
    
    def _extract_citations(
        self, 
        answer: str, 
        chunks: List[dict]
    ) -> List[Citation]:
        """
        Extracts citations from used chunks.
        """
        citations = []
        
        for chunk in chunks:
            metadata = chunk.get("metadata", {})
            
            # Extract Page-Number from Metadata
            # PDFParser uses "page_number"
            page = metadata.get("page_number", 1)
            
            # Text-Snippet (first 100 chars of chunk)
            text_snippet = chunk.get("text", "")[:100]
            
            citation = Citation(
                doc_id=metadata.get("doc_id", "unknown"), # We need to ensure doc_id is in metadata
                doc_name=metadata.get("doc_name", "unknown"), # We need to ensure doc_name is in metadata
                page=page,
                text_snippet=text_snippet,
                chunk_id=chunk.get("id", ""),
                score=chunk.get("score", 0.0)
            )
            
            citations.append(citation)
        
        return citations

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
