from typing import List, Optional
from src.parsers.models import Document
from src.rag.models import Chunk

class Chunker:
    """
    Splits documents into semantic chunks while preserving metadata.
    Optimized for German text structures.
    """
    def __init__(
        self, 
        chunk_size: int = 500, 
        chunk_overlap: int = 50,
        separators: Optional[List[str]] = None
    ):
        """
        Initialize the Chunker.
        
        Args:
            chunk_size: Maximum number of tokens/characters per chunk.
            chunk_overlap: Number of tokens/characters to overlap between chunks.
            separators: List of separators to use for splitting (in order of priority).
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        # Default separators for recursive splitting: Paragraphs, Lines, Sentences, Words
        # Note: ". " is important for German sentence boundaries
        self.separators = separators or ["\n\n", "\n", ". ", " ", ""]

    def split(self, document: Document) -> List[Chunk]:
        """
        Splits a document into chunks.
        
        Args:
            document: The parsed document to split.
            
        Returns:
            List[Chunk]: A list of Chunk objects with metadata preserved.
        """
        # Placeholder implementation for Task 6
        # Actual recursive splitting logic will be implemented in Task 7
        return []
