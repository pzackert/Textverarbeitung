"""
Real-world validation of Chunking with actual IFB documents.
Tests the complete Parser -> Chunker pipeline.
"""
import pytest
from pathlib import Path
import sys
import os

# Add project root to path to ensure imports work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))

from src.parsers.pdf_parser import PDFParser
from src.parsers.docx_parser import DocxParser
from src.parsers.xlsx_parser import XlsxParser
from src.rag.chunker import Chunker
from src.parsers.models import Document

# Define paths to test documents (using option_1_mvp data as source)
# Adjusting path to point to the actual location found in the workspace
WORKSPACE_ROOT = Path("/Users/patrick.zackert/projects/masterprojekt")
TEST_DATA_DIR = WORKSPACE_ROOT / "option_1_mvp/data/input/D_Test"

PDF_FILE = TEST_DATA_DIR / "IFB_Foerderantrag_Smart_Port_Analytics.pdf"
DOCX_FILE = TEST_DATA_DIR / "Projektskizze_Smart_Port_Analytics.docx"
XLSX_FILE = TEST_DATA_DIR / "Businessplan_Smart_Port_Analytics.xlsx"

def analyze_chunks(chunks, doc_type):
    """Analyze chunk quality metrics."""
    if not chunks:
        return {
            "total_chunks": 0,
            "avg_chunk_size": 0,
            "min_chunk_size": 0,
            "max_chunk_size": 0,
            "total_content_size": 0,
            "contains_umlauts": False
        }
        
    metrics = {
        "doc_type": doc_type,
        "total_chunks": len(chunks),
        "avg_chunk_size": sum(len(c.content) for c in chunks) / len(chunks),
        "min_chunk_size": min(len(c.content) for c in chunks),
        "max_chunk_size": max(len(c.content) for c in chunks),
        "total_content_size": sum(len(c.content) for c in chunks),
        # Check for German characters
        "contains_umlauts": any('ä' in c.content or 'ö' in c.content 
                                or 'ü' in c.content or 'ß' in c.content 
                                for c in chunks),
    }
    return metrics

class TestRealWorldChunking:
    """Integration tests with real IFB documents."""
    
    def test_pdf_document_chunking(self):
        """Test chunking of real PDF document."""
        if not PDF_FILE.exists():
            pytest.skip(f"PDF test file not found at {PDF_FILE}")
            
        print(f"\nTesting PDF: {PDF_FILE.name}")
        
        # 1. Parse PDF
        parser = PDFParser()
        documents = parser.parse(str(PDF_FILE))
        assert len(documents) > 0
        print(f"Parsed {len(documents)} document(s) from PDF")
        
        # 2. Chunk the document
        chunker = Chunker(chunk_size=500, chunk_overlap=50)
        all_chunks = []
        for doc in documents:
            chunks = chunker.split(doc)
            all_chunks.extend(chunks)
            
        # 3. Validate chunks
        assert len(all_chunks) > 0
        print(f"Created {len(all_chunks)} chunks from PDF")
        
        # 4. Print statistics
        metrics = analyze_chunks(all_chunks, "PDF")
        print(f"PDF Metrics: {metrics}")
        
        # Assertions
        assert metrics["avg_chunk_size"] <= 500
        assert metrics["max_chunk_size"] <= 500
        assert metrics["contains_umlauts"] is True # Assuming German text
        
        # Check metadata inheritance
        assert all_chunks[0].metadata.get("source") == str(PDF_FILE)
        assert all_chunks[0].metadata.get("doc_type") == "pdf"

    def test_docx_document_chunking(self):
        """Test chunking of real DOCX document."""
        if not DOCX_FILE.exists():
            pytest.skip(f"DOCX test file not found at {DOCX_FILE}")
            
        print(f"\nTesting DOCX: {DOCX_FILE.name}")
        
        # 1. Parse DOCX
        parser = DocxParser()
        documents = parser.parse(str(DOCX_FILE))
        assert len(documents) > 0
        print(f"Parsed {len(documents)} document(s) from DOCX")
        
        # 2. Chunk the document
        chunker = Chunker(chunk_size=500, chunk_overlap=50)
        all_chunks = []
        for doc in documents:
            chunks = chunker.split(doc)
            all_chunks.extend(chunks)
            
        # 3. Validate chunks
        assert len(all_chunks) > 0
        print(f"Created {len(all_chunks)} chunks from DOCX")
        
        # 4. Print statistics
        metrics = analyze_chunks(all_chunks, "DOCX")
        print(f"DOCX Metrics: {metrics}")
        
        # Assertions
        assert metrics["avg_chunk_size"] <= 500
        assert metrics["max_chunk_size"] <= 500
        
        # Check metadata inheritance
        assert all_chunks[0].metadata.get("source") == str(DOCX_FILE)
        assert all_chunks[0].metadata.get("doc_type") == "docx"

    def test_xlsx_document_chunking(self):
        """Test chunking of real XLSX document."""
        if not XLSX_FILE.exists():
            pytest.skip(f"XLSX test file not found at {XLSX_FILE}")
            
        print(f"\nTesting XLSX: {XLSX_FILE.name}")
        
        # 1. Parse XLSX
        parser = XlsxParser()
        documents = parser.parse(str(XLSX_FILE))
        assert len(documents) > 0
        print(f"Parsed {len(documents)} document(s) from XLSX")
        
        # 2. Chunk the document
        chunker = Chunker(chunk_size=500, chunk_overlap=50)
        all_chunks = []
        for doc in documents:
            chunks = chunker.split(doc)
            all_chunks.extend(chunks)
            
        # 3. Validate chunks
        assert len(all_chunks) > 0
        print(f"Created {len(all_chunks)} chunks from XLSX")
        
        # 4. Print statistics
        metrics = analyze_chunks(all_chunks, "XLSX")
        print(f"XLSX Metrics: {metrics}")
        
        # Assertions
        assert metrics["avg_chunk_size"] <= 500
        assert metrics["max_chunk_size"] <= 500
        
        # Check metadata inheritance
        assert all_chunks[0].metadata.get("source") == str(XLSX_FILE)
        assert all_chunks[0].metadata.get("doc_type") == "xlsx"
