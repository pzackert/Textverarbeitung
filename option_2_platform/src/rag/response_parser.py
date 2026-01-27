import logging
import os
import re
from typing import List, Dict, Any, Set

logger = logging.getLogger(__name__)


class ResponseParser:
    """Parse and structure LLM responses."""

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
                source_path = metadata.get("source", "Unknown")
                # Fix: Extract filename from path for clean display
                doc_name = os.path.basename(source_path) if source_path != "Unknown" else "Dokument"
                
                mapped.append({
                    "number": num,
                    "source": source_path,
                    "doc_name": doc_name,  # Explicitly send filename
                    "page": metadata.get("page_number") or metadata.get("page") or 1, # Robust page extraction
                    "score": source.get("score", 0.0)
                })
            else:
                logger.warning(f"Citation [Quelle {num}] out of range (max {len(sources)})")
                
        return mapped

    def format_sources_list(self, sources: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Normalize sources without additional filtering; preserve metadata."""
        formatted: List[Dict[str, Any]] = []
        for s in sources or []:
            metadata = s.get("metadata", {}) if isinstance(s, dict) else {}

            source_path = metadata.get("source") or s.get("source") or s.get("dokument") or "Unknown"
            doc_name = (
                s.get("doc_name")
                or metadata.get("doc_name")
                or metadata.get("document")
                or metadata.get("dokument")
            )
            if not doc_name and source_path != "Unknown":
                doc_name = os.path.basename(source_path)
            doc_name = doc_name or "Dokument"

            page = (
                s.get("page")
                or s.get("page_number")
                or metadata.get("page_number")
                or metadata.get("page")
                or 1
            )
            try:
                page = int(page)
            except Exception:
                page = 1

            chunk_id = s.get("chunk_id") or metadata.get("chunk_id") or s.get("id")
            text_snippet = (
                s.get("text_snippet")
                or s.get("content")
                or s.get("text")
                or metadata.get("text")
                or ""
            )
            if isinstance(text_snippet, str):
                text_snippet = text_snippet[:240]
            else:
                text_snippet = None

            formatted.append({
                "doc_name": doc_name,
                "source": source_path,
                "page": page,
                "score": s.get("score", 0.0),
                "chunk_id": chunk_id,
                "text_snippet": text_snippet,
                "metadata": metadata,
            })

        return formatted

    def parse(self, response: str, sources: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Parse LLM response and map citations to sources without mutating structure."""
        citation_numbers = self.extract_citations(response)
        mapped_citations = self.map_citations(citation_numbers, sources)
        clean_sources = self.format_sources_list(sources)

        return {
            "answer": response,
            "citation_numbers": list(citation_numbers),
            "citations": mapped_citations,
            "sources": clean_sources,
        }
