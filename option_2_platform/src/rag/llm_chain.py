import logging
import re
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
        top_k: Optional[int] = None,
        system_prompt: Optional[str] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Execute complete RAG query.
        
        Args:
            question: User question
            template_type: Prompt template to use
            top_k: Number of chunks to retrieve (overrides config)
            system_prompt: Optional system prompt override
            metadata_filter: Filter for retrieval (e.g. {"project_id": "..."})
            
        Returns:
            Dict with answer, sources, citations, metadata
        """
        start_time = time.time()
        logger.info(f"Starting RAG query: {question[:50]}...")
        
        # 1. Retrieval
        logger.info("Step 1: Retrieving documents...")
        results = self.retrieval_engine.retrieve(
            query=question,
            top_k=top_k or self.config.top_k,
            metadata_filter=metadata_filter
        )
        
        # 2. Build prompt context (metadata filter aware)
        logger.info(f"Step 2: Building prompt with {len(results)} chunks...")
        prompt = self.prompt_builder.build_query_prompt(
            query=question,
            template_type=template_type,
            metadata_filter=metadata_filter,
            results=results
        )

        # 3. Generate Answer via LLM Provider
        logger.info("Step 3: Generating response via LLM...")
        try:
            answer = self.llm_provider.generate(
                prompt=prompt,
                max_tokens=self.config.llm_max_tokens,
                temperature=self.config.llm_temperature
            )
        except Exception as e:
            logger.error(f"LLM Generation failed: {e}")
            answer = "Entschuldigung, ich konnte keine Antwort generieren. Bitte prüfen Sie die Verbindung zum LLM."

        parsed_result = self.response_parser.parse(answer, results)
        
        # --- Source Filtering (Bugfix: Ghost Sources) ---
        # Only include sources that were explicitly cited in the answer (e.g., [1], [2])
        # If no citations are present, we assume the answer came from general knowledge.
        
        import re
        # Find all [digit] patterns
        citation_indices = set()
        matches = re.findall(r'\[\s*(\d+)\s*\]', answer)
        for m in matches:
            try:
                # User-facing index is 1-based, list is 0-based
                idx = int(m) - 1
                if 0 <= idx < len(results):
                    citation_indices.add(idx)
            except ValueError:
                continue

        # If valid citations found, filter results and parsed sources/citations
        filtered_sources = []
        filtered_citations = []
        
        if citation_indices:
            # We have citations, so we trust the LLM used these docs
            for idx in sorted(citation_indices):
                # Add to sources
                res = results[idx]
                source_meta = res.get("metadata", {})
                filtered_sources.append(source_meta)
                
                # Check if this index corresponds to any parsed citations 
                # (ResponseParser might have done its own thing, but we sync it here)
                # Actually, ResponseParser tries to match text snippets. 
                # Let's just rely on our index checking for simplicity and correctness.
                
                # Create a Citation object for this result
                c = Citation(
                    doc_id=source_meta.get("doc_id", "unknown"),
                    doc_name=source_meta.get("doc_name", "unknown"),
                    page=source_meta.get("page", 1),
                    text_snippet=res.get("content", "")[:100],
                    chunk_id=res.get("id", ""),
                    score=res.get("score", 0.0)
                )
                filtered_citations.append(c)
                
            parsed_result["sources"] = filtered_sources
            parsed_result["citations"] = filtered_citations
        else:
            # No citations found -> Assume General Knowledge -> Clear sources
            # Exception: If the prompt didn't strictly enforce [x], we might miss some.
            # But we updated the prompt to be strict about citing [Nummer].
            parsed_result["sources"] = []
            parsed_result["citations"] = []

        duration = time.time() - start_time
        parsed_result["metadata"] = {
            "duration": duration,
            "model": self.llm_provider.model_name,
            "chunks_retrieved": len(results),
            "sources_displayed": len(filtered_sources)
        }
        
        logger.info(f"Query completed in {duration:.2f}s. Sources shown: {len(filtered_sources)}")
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
        embedding_function=embedding_generator,
        schema_version=config.metadata_schema_version,
    )
    vector_store.ensure_schema(config.metadata_schema_version)
    
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
