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
        threshold = self.config.similarity_threshold  # e.g. 0.35 (lower is stricter for cosine distance in Chroma, higher for similarity. Wait.)
        # Chroma using "cosine" space: distance = 1 - similarity.
        # VectorStore.query converts to "score" (similarity).
        # So score close to 1.0 is good.
        # Threshold should be minimum similarity. e.g. 0.7
        
        # User config says: similarity_threshold: 0.35
        # If config value is low (0.35), it implies cosine DISTANCE threshold?
        # Let's check config.yaml again.
        # "similarity_threshold: 0.35 # Lower means stricter matching" -> This comment in config implies DISTANCE.
        # If it says "Lower means stricter", it MUST be Distance. (0 = exact match).
        # VectorStore returns "score" which it calculates as 1 - distance.
        # So Similarity Score = 1 - Distance.
        # If user sets Threshold 0.35 (Distance), that means Similarity > (1 - 0.35) = 0.65.
        
        # Let's read config comment to be sure.
        # Assuming config.similarity_threshold is DISTANCE (because of "Lower means stricter").
        
        # Handle hybrid filtering (Project + Global)
        # If metadata_filter contains 'include_global': True, we must query broadly then filter in Python
        # because ChromaDB (v0.4.x) simple where logic might be tricky for "Exists OR Not Exists".
        
        include_global = False
        active_filter = metadata_filter
        target_project_id = None
        
        if metadata_filter and metadata_filter.get("include_global"):
            include_global = True
            target_project_id = metadata_filter.get("project_id")
            # Remove from filter passed to Chroma, to search broadly
            # We assume if we want global, we shouldn't restrict by project_id in DB query yet
            active_filter = {k: v for k, v in metadata_filter.items() if k not in ["include_global", "project_id"]}
            if not active_filter:
                active_filter = None
                
        # Fetch more candidates if filtering manually
        fetch_k = (top_k * 3) if include_global else top_k
        
        results = self.vector_store.query(
            query_text=query,
            top_k=fetch_k,
            metadata_filter=active_filter
        )
        
        # Post-Processing for Hybrid Security
        if include_global:
            secure_results = []
            for r in results:
                pid = r.get("metadata", {}).get("project_id")
                # Allowed if it matches target project OR is global (no project_id)
                if pid == target_project_id or pid is None:
                    secure_results.append(r)
            results = secure_results[:top_k]
        
        # Filter by threshold if set
        if threshold is not None:
             # Interpreting threshold as Distance Threshold (0.35).
             # We want Results where Distance <= Threshold.
             # VectorStore returns 'score' = 1 - Distance.
             # So Distance = 1 - score.
             # Condition: (1 - score) <= threshold
             # score >= 1 - threshold
             
             min_score = 1.0 - threshold
             filtered_results = [r for r in results if r.get("score", 0) >= min_score]
             
             if len(filtered_results) < len(results):
                 logger.info(f"Filtered {len(results) - len(filtered_results)} chunks below similarity {(1-threshold):.2f}")
             
             results = filtered_results
        
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
