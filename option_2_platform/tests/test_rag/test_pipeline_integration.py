import pytest
from pathlib import Path
import time
from src.parsers.pdf_parser import PDFParser
from src.rag.chunker import Chunker
from src.rag.embeddings import EmbeddingGenerator

# Define paths
WORKSPACE_ROOT = Path("/Users/patrick.zackert/projects/masterprojekt")
TEST_DATA_DIR = WORKSPACE_ROOT / "option_1_mvp/data/input/D_Test"
PDF_FILE = TEST_DATA_DIR / "IFB_Foerderantrag_Smart_Port_Analytics.pdf"

class TestPipelineIntegration:
    """
    Integration tests for the full RAG pipeline:
    Document -> Parser -> Chunker -> EmbeddingGenerator
    """
    
    def test_full_pipeline_flow(self):
        """Test the complete flow from document to embeddings."""
        if not PDF_FILE.exists():
            pytest.skip(f"Test file not found: {PDF_FILE}")
            
        print(f"\n--- Starting Pipeline Integration Test ---")
        print(f"File: {PDF_FILE.name}")
        
        # 1. Parsing
        print("\n1. Parsing Document...")
        start_time = time.time()
        parser = PDFParser()
        documents = parser.parse(str(PDF_FILE))
        parse_time = time.time() - start_time
        
        assert len(documents) > 0
        print(f"Parsed {len(documents)} documents in {parse_time:.4f}s")
        
        # 2. Chunking
        print("\n2. Chunking Documents...")
        start_time = time.time()
        chunker = Chunker(chunk_size=500, chunk_overlap=50)
        all_chunks = []
        for doc in documents:
            chunks = chunker.split(doc)
            all_chunks.extend(chunks)
        chunk_time = time.time() - start_time
        
        assert len(all_chunks) > 0
        print(f"Generated {len(all_chunks)} chunks in {chunk_time:.4f}s")
        print(f"Average chunk size: {sum(len(c.content) for c in all_chunks)/len(all_chunks):.1f} chars")
        
        # 3. Embedding
        print("\n3. Generating Embeddings...")
        start_time = time.time()
        embedder = EmbeddingGenerator("paraphrase-multilingual-MiniLM-L12-v2")
        
        # Extract text content from chunks
        chunk_texts = [chunk.content for chunk in all_chunks]
        
        # Generate embeddings in batch
        embeddings = embedder.embed_batch(chunk_texts)
        embed_time = time.time() - start_time
        
        print(f"Generated {len(embeddings)} embeddings in {embed_time:.4f}s")
        
        # 4. Verification
        print("\n4. Verifying Results...")
        
        # Count match
        assert len(embeddings) == len(all_chunks)
        print("✅ Count check passed")
        
        # Dimension check
        assert len(embeddings[0]) == 384
        print("✅ Dimension check passed (384)")
        
        # Content check (ensure not empty)
        assert not any(all(x == 0 for x in emb) for emb in embeddings)
        print("✅ Content check passed")
        
        # Performance summary
        total_time = parse_time + chunk_time + embed_time
        print(f"\n--- Pipeline Summary ---")
        print(f"Total Time: {total_time:.4f}s")
        print(f"Time per chunk: {total_time/len(all_chunks):.4f}s")
