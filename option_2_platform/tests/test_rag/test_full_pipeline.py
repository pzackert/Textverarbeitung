import pytest
import shutil
import tempfile
from pathlib import Path
import sys

# Ensure src is in path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

from src.rag.ingestion import IngestionPipeline
from src.rag.retrieval import RetrievalEngine
from src.rag.config import RAGConfig

@pytest.fixture
def temp_rag_dir():
    """Create temporary directory for RAG data."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def test_config(temp_rag_dir):
    """Create RAG config using temp directory."""
    return RAGConfig(
        persist_directory=str(Path(temp_rag_dir) / "chromadb"),
        vector_store_path=str(Path(temp_rag_dir) / "chromadb"),
        collection_name="test_e2e_collection"
    )

@pytest.fixture
def sample_pdf(temp_rag_dir):
    """Copy a sample PDF to temp dir."""
    # Source PDF from option_1_mvp (assuming it exists based on file_search)
    # We are in option_2_platform, so we need to go up one level
    source_pdf = Path("../option_1_mvp/data/input/A_Perfekter Fall/Dokument.pdf")
    if not source_pdf.exists():
        # Try absolute path as fallback or check if we are in root
        source_pdf = Path("option_1_mvp/data/input/A_Perfekter Fall/Dokument.pdf")
        
    if not source_pdf.exists():
        pytest.skip(f"Sample PDF not found at {source_pdf}")
    
    dest_pdf = Path(temp_rag_dir) / "test_doc.pdf"
    shutil.copy(source_pdf, dest_pdf)
    return dest_pdf

def test_end_to_end_rag_pipeline(test_config, sample_pdf):
    """Test complete RAG pipeline: Ingest + Retrieve."""
    # 1. Ingest documents
    pipeline = IngestionPipeline(config=test_config)
    result = pipeline.ingest_file(str(sample_pdf))
    
    assert result['success']
    assert result['document_count'] == 1
    assert result['chunk_count'] > 0
    
    # 2. Retrieve
    # Re-initialize vector store/retrieval to ensure persistence works (optional but good)
    # But here we can just use the pipeline's vector store or create a new RetrievalEngine
    retrieval = RetrievalEngine(pipeline.vector_store, config=test_config)
    
    # Query something likely to be in the document
    # "Dokument.pdf" from "A_Perfekter Fall" likely contains "Projekt" or "Förderung"
    response = retrieval.retrieve_and_format("Projekt")
    
    # 3. Verify
    assert response['num_results'] > 0
    assert len(response['context']) > 0
    assert response['query'] == "Projekt"
