import re
import logging
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)

class ResponseParser:
    """Parse and structure LLM responses."""
    
    def parse(self, response: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Parse LLM response and map citations to sources.
        
        Args:
            response: Raw text response from LLM
            sources: List of source documents used in context
            
        Returns:
            Structured dictionary with answer, citations, and metadata
        """
        citation_numbers = self.extract_citations(response)
        mapped_citations = self.map_citations(citation_numbers, sources)
        
        return {
            "answer": response,
            "citation_numbers": list(citation_numbers),
            "citations": mapped_citations,
            "sources": sources  # All available sources
        }
        
    def extract_citations(self, text: str) -> Set[int]:
        """
        Find [Quelle X] patterns using regex.
        Handles: [Quelle 1], [Quelle 1, 2], [Quelle 1,2]
        
        Returns:
            Set of unique citation numbers found in text
        """
        citations = set()
        
        # Pattern for [Quelle 1] or [Quelle 1, 2]
        # Matches "Quelle " followed by numbers and commas/spaces inside brackets
        pattern = r"\[Quelle\s+([\d,\s]+)\]"
        
        matches = re.finditer(pattern, text)
        for match in matches:
            numbers_str = match.group(1)
            # Split by comma and clean up
            parts = [p.strip() for p in numbers_str.split(',')]
            for part in parts:
                if part.isdigit():
                    citations.add(int(part))
                    
        return citations
        
    def map_citations(self, citation_numbers: Set[int], sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map citation numbers to source metadata.
        
        Args:
            citation_numbers: Set of citation indices (1-based)
            sources: List of source documents (0-indexed)
            
        Returns:
            List of cited source metadata
        """
        mapped = []
        for num in sorted(citation_numbers):
            # Convert 1-based citation to 0-based index
            idx = num - 1
            if 0 <= idx < len(sources):
                source = sources[idx]
                metadata = source.get("metadata", {})
                mapped.append({
                    "number": num,
                    "source": metadata.get("source", "Unknown"),
                    "page": metadata.get("page"),
                    "score": source.get("score")
                })
            else:
                logger.warning(f"Citation [Quelle {num}] out of range (max {len(sources)})")
                
        return mapped
