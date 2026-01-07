from typing import List, Dict, Any, Optional
import logging
from .prompts import PromptTemplate, format_context
from .retrieval import RetrievalEngine
from .config import RAGConfig

logger = logging.getLogger(__name__)

class PromptBuilder:
    """
    Service for building prompts from retrieval results.
    Integrates retrieval engine and prompt templates.
    """
    
    def __init__(self, retrieval_engine: RetrievalEngine):
        """Initialize with retrieval engine."""
        self.retrieval_engine = retrieval_engine
        self.config = RAGConfig.from_yaml()
        
    def build_query_prompt(
        self,
        query: str,
        template_type: str = "standard",
        metadata_filter: Optional[Dict[str, Any]] = None,
        results: Optional[List[Dict[str, Any]]] = None,
        system_prompt: Optional[str] = None
    ) -> str:
        """
        Build complete prompt for query.
        Retrieves context (if not provided) and formats prompt.
        
        Args:
            query: User query or criteria
            template_type: Type of template to use
            metadata_filter: Optional filters for retrieval
            results: Pre-retrieved results (optional optimization)
            
        Returns:
            Formatted prompt string ready for LLM
        """
        # 1. Select Template
        if template_type == "standard":
            template = PromptTemplate.standard_query()
        elif template_type == "evaluation":
            template = PromptTemplate.criteria_evaluation()
        elif template_type == "summary":
            template = PromptTemplate.document_summary()
        else:
            logger.warning(f"Unknown template type '{template_type}', using standard.")
            template = PromptTemplate.standard_query()
            
        # 2. Retrieve Context
        if results is None:
            results = self.retrieval_engine.retrieve(
                query=query,
                top_k=self.config.top_k, 
                metadata_filter=metadata_filter
            )
        
        # 3. Limit number of chunks to avoid overlong prompts
        max_chunks = self.config.max_context_chunks or len(results)
        results = results[:max_chunks]

        # 4. Format Context (trim each chunk to keep prompt small)
        context_str = format_context(results, include_scores=False, max_chars=800) # Config could be used here
        
        if not context_str:
            context_str = "Keine relevanten Dokumente gefunden."
            
        # 5. Format Prompt
        prompt = template.format(
            query=query, 
            context=context_str,
            system_prompt_override=system_prompt
        )
        
        return prompt
