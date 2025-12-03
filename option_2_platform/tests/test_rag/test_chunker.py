import pytest
from src.rag.chunker import Chunker
from src.parsers.models import Document
from src.rag.models import Chunk

GERMAN_TEXT = """
Dies ist ein deutscher Testtext für das Chunking-System. 
Er enthält mehrere Sätze mit Umlauten wie ä, ö, ü und ß.
Die Hamburgische Investitions- und Förderbank (IFB) prüft Förderanträge.
Innovationsprojekte werden nach verschiedenen Kriterien bewertet.
"""

class TestChunker:
    """Test suite for Chunker class."""
    
    def test_basic_string_chunking(self):
        """Test basic chunking with string input."""
        chunker = Chunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.split(GERMAN_TEXT)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 0
        assert isinstance(chunks[0], Chunk)
        assert len(chunks[0].content) <= 100
        
    def test_chunk_size_limit(self):
        """Test that chunks respect size limit."""
        chunker = Chunker(chunk_size=50, chunk_overlap=10)
        chunks = chunker.split(GERMAN_TEXT)
        
        for chunk in chunks:
            assert len(chunk.content) <= 50
            
    def test_overlap_functionality(self):
        """Test chunk overlap."""
        # Use a text where overlap is predictable
        text = "1234567890" * 2  # 20 chars
        # chunk_size=10, overlap=5
        # Expected roughly: "1234567890" (10), "6789012345" (10)...
        chunker = Chunker(chunk_size=12, chunk_overlap=4)
        chunks = chunker.split(text)
        
        assert len(chunks) > 1
        assert chunks[0].metadata['chunk_overlap'] == 4
        
        # Check that we have some content
        assert len(chunks[0].content) <= 12
        
    def test_document_input(self):
        """Test chunking with Document object."""
        doc = Document(
            content=GERMAN_TEXT,
            metadata={"author": "Test Author", "year": 2025},
            source_file="test_doc.pdf",
            file_type="pdf"
        )
        
        chunker = Chunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.split(doc)
        
        assert len(chunks) > 0
        first_chunk = chunks[0]
        
        # Check inherited metadata
        assert first_chunk.metadata["author"] == "Test Author"
        assert first_chunk.metadata["year"] == 2025
        assert first_chunk.metadata["source"] == "test_doc.pdf"
        assert first_chunk.metadata["doc_type"] == "pdf"
        
    def test_metadata_enrichment(self):
        """Test chunk metadata."""
        chunker = Chunker(chunk_size=100, chunk_overlap=20)
        chunks = chunker.split(GERMAN_TEXT)
        
        total = len(chunks)
        for i, chunk in enumerate(chunks):
            assert chunk.metadata["chunk_id"] == i
            assert chunk.metadata["chunk_index"] == i
            assert chunk.metadata["total_chunks"] == total
            assert chunk.metadata["chunk_size"] == 100
            assert chunk.metadata["chunk_overlap"] == 20
            
    def test_german_text(self):
        """Test with German language."""
        # Test specifically that umlauts are preserved and not mangled
        text = "Übermäßiger Ölkonsum ist schädlich."
        chunker = Chunker(chunk_size=50, chunk_overlap=10)
        chunks = chunker.split(text)
        
        # Check if the first chunk contains correct characters
        assert "Übermäßiger" in chunks[0].content
        assert "Ölkonsum" in chunks[0].content
        
    def test_edge_cases(self):
        """Test edge cases."""
        chunker = Chunker(chunk_size=100, chunk_overlap=20)
        
        # Empty string
        assert chunker.split("") == []
        
        # Short text
        short_text = "Short."
        chunks = chunker.split(short_text)
        assert len(chunks) == 1
        assert chunks[0].content == "Short."
        
        # No separators (long string of chars)
        long_char_string = "a" * 200
        chunks_long = chunker.split(long_char_string)
        assert len(chunks_long) > 1
        assert len(chunks_long[0].content) <= 100
        
    def test_separator_strategy(self):
        """Test that separators are respected."""
        # Paragraphs
        text = "Para1.\n\nPara2.\n\nPara3."
        # If chunk size is small enough to split paragraphs but large enough to hold one
        chunker = Chunker(chunk_size=10, chunk_overlap=0) 
        
        chunks = chunker.split(text)
        # Ideally we get 3 chunks because of \n\n split
        # "Para1." is 6 chars. 
        assert len(chunks) >= 3
        assert "Para1." in chunks[0].content
