"""
Retrieval Engine for RAG system.
Handles query processing and context assembly for LLM.
"""
from typing import List, Dict, Any, Optional
import logging

from .vector_store import VectorStore
from .embeddings import EmbeddingGenerator
from .config import RAGConfig

logger = logging.getLogger(__name__)

class RetrievalEngine:
    """
    Retrieval engine for semantic search and context assembly.
    
    Handles:
    - Query processing
    - Semantic search
    - Result ranking
    - Context formatting for LLM
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        config: Optional[RAGConfig] = None
    ):
        """Initialize retrieval engine."""
        self.vector_store = vector_store
        self.config = config or RAGConfig.from_yaml()
    
    def retrieve(
        self,
        query: str,
        top_k: Optional[int] = None,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant chunks for query.
        
        Args:
            query: User query text
            top_k: Number of results (default from config)
            metadata_filter: Optional metadata filters
            
        Returns:
            List of relevant chunks with metadata and scores
        """
        top_k = top_k or self.config.top_k
        
        # Query vector store
        results = self.vector_store.query(
            query_text=query,
            top_k=top_k,
            metadata_filter=metadata_filter
        )
        
        return results
    
    def format_context(self, results: List[Dict[str, Any]]) -> str:
        """
        Format retrieval results into context string for LLM.
        
        Args:
            results: List of retrieval results
            
        Returns:
            Formatted context string
        """
        context_parts = []
        
        for i, result in enumerate(results, 1):
            metadata = result.get('metadata', {})
            source = (
                metadata.get('doc_name')
                or metadata.get('source')
                or metadata.get('source_file', 'Unknown')
            )
            content = result.get('content', '')
            score = result.get('score', 0.0)
            
            context_part = f"""
[Quelle {i}: {source}]
{content}
"""
            context_parts.append(context_part.strip())
        
        return "\n\n".join(context_parts)
    
    def retrieve_and_format(
        self,
        query: str,
        top_k: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Retrieve and format in one step.
        
        Returns:
            Dictionary with results and formatted context
        """
        results = self.retrieve(query, top_k)
        context = self.format_context(results)
        
        return {
            'query': query,
            'results': results,
            'context': context,
            'num_results': len(results)
        }
