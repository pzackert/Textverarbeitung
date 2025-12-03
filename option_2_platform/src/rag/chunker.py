from typing import List, Optional, Union
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

    def split(self, document: Union[Document, str]) -> List[str]:
        """
        Splits a document into text chunks.
        
        Args:
            document: The parsed document or text string to split.
            
        Returns:
            List[str]: A list of text chunks.
        """
        if isinstance(document, str):
            text = document
        else:
            text = document.content
            
        return self._split_text(text, self.separators)

    def _split_text(self, text: str, separators: List[str]) -> List[str]:
        """
        Recursively splits text using the provided separators.
        """
        final_chunks = []
        
        # Find the appropriate separator
        separator = separators[-1]
        new_separators = []
        
        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1:]
                break
                
        # Split text
        if separator:
            splits = text.split(separator)
        else:
            splits = list(text) # Split by character
            
        # Merge splits into chunks
        final_chunks = []
        good_splits = []
        
        for s in splits:
            if len(s) < self.chunk_size:
                good_splits.append(s)
            else:
                if good_splits:
                    merged = self._merge_splits(good_splits, separator)
                    final_chunks.extend(merged)
                    good_splits = []
                if new_separators:
                    final_chunks.extend(self._split_text(s, new_separators))
                else:
                    # No more separators, force split
                    final_chunks.append(s[:self.chunk_size]) # Simple truncation for now
                    
        if good_splits:
            merged = self._merge_splits(good_splits, separator)
            final_chunks.extend(merged)
            
        return final_chunks

    def _merge_splits(self, splits: List[str], separator: str) -> List[str]:
        """
        Merges small splits into chunks of max size with overlap.
        """
        docs = []
        current_doc = []
        total = 0
        separator_len = len(separator)
        
        for d in splits:
            _len = len(d)
            
            # Can we add this split to the current chunk?
            if total + _len + (separator_len if current_doc else 0) > self.chunk_size:
                if total > self.chunk_size:
                    # Warning: current chunk is already too big (shouldn't happen with correct logic)
                    pass
                
                if current_doc:
                    doc = separator.join(current_doc)
                    if doc:
                        docs.append(doc)
                    
                    # Handle overlap
                    # We want to keep the tail of current_doc that fits in chunk_overlap
                    while total > self.chunk_overlap or (total + _len + separator_len > self.chunk_size and total > 0):
                        total -= len(current_doc[0]) + (separator_len if len(current_doc) > 1 else 0)
                        current_doc.pop(0)
            
            current_doc.append(d)
            total += _len + (separator_len if len(current_doc) > 1 else 0)
            
        if current_doc:
            doc = separator.join(current_doc)
            if doc:
                docs.append(doc)
                
        return docs
