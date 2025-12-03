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
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Build complete prompt for query.
        Retrieves context and formats prompt.
        
        Args:
            query: User query or criteria
            template_type: Type of template to use ("standard", "evaluation", "summary")
            metadata_filter: Optional filters for retrieval
            
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
        # For summary, we might want to retrieve differently (e.g. all chunks of a doc),
        # but for now we use standard retrieval.
        results = self.retrieval_engine.retrieve(
            query=query,
            top_k=self.config.top_k, # Use config top_k
            metadata_filter=metadata_filter
        )
        
        # 3. Format Context
        context_str = format_context(results, include_scores=False) # Config could be used here
        
        if not context_str:
            context_str = "Keine relevanten Dokumente gefunden."
            
        # 4. Format Prompt
        prompt = template.format(query=query, context=context_str)
        
        return prompt
