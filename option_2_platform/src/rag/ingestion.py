"""
Document Ingestion Pipeline Service.
Orchestrates: Document → Parser → Chunker → Embeddings → Vector Store
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from src.parsers.pdf_parser import PDFParser
from src.parsers.docx_parser import DocxParser
from src.parsers.xlsx_parser import XlsxParser
from src.parsers.models import Document
from .chunker import Chunker
from .embeddings import EmbeddingGenerator
from .vector_store import VectorStore
from .config import RAGConfig

logger = logging.getLogger(__name__)

class IngestionPipeline:
    """
    Complete document ingestion pipeline.
    
    Handles:
    - File type detection
    - Document parsing
    - Text chunking
    - Embedding generation
    - Vector store insertion
    """
    
    def __init__(self, config: Optional[RAGConfig] = None):
        """
        Initialize ingestion pipeline with configuration.
        
        Args:
            config: RAG configuration (uses default if None)
        """
        self.config = config or RAGConfig.from_yaml()
        
        # Initialize components
        self._init_parsers()
        self._init_chunker()
        self._init_embedder()
        self._init_vector_store()
    
    def _init_parsers(self):
        """Initialize document parsers."""
        self.parsers = {
            '.pdf': PDFParser(),
            '.docx': DocxParser(),
            '.xlsx': XlsxParser(),
        }
    
    def _init_chunker(self):
        """Initialize chunker with config."""
        self.chunker = Chunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
        )
    
    def _init_embedder(self):
        """Initialize embedding generator."""
        self.embedder = EmbeddingGenerator(
            model_name=self.config.embedding_model
        )
    
    def _init_vector_store(self):
        """Initialize vector store."""
        self.vector_store = VectorStore(
            collection_name=self.config.collection_name,
            persist_directory=self.config.vector_store_path,
            embedding_function=self.embedder
        )
    
    def ingest_file(self, file_path: str) -> Dict[str, Any]:
        """
        Ingest a single file through complete pipeline.
        
        Args:
            file_path: Path to document file
            
        Returns:
            Ingestion results with statistics
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # 1. Parse document
        documents = self._parse_document(path)
        
        # 2. Chunk document
        chunks = self._chunk_document(documents)
        
        # 3. Store chunks (embeddings generated automatically)
        chunk_ids = self._store_chunks(chunks)
        
        # 4. Return statistics
        return {
            'file_path': str(path),
            'file_type': path.suffix,
            'document_count': 1,
            'chunk_count': len(chunks),
            'chunk_ids': chunk_ids,
            'success': True
        }
    
    def ingest_directory(self, directory_path: str) -> List[Dict[str, Any]]:
        """
        Ingest all supported documents from a directory.
        
        Args:
            directory_path: Path to directory
            
        Returns:
            List of ingestion results for each file
        """
        directory = Path(directory_path)
        if not directory.exists():
             raise FileNotFoundError(f"Directory not found: {directory_path}")

        results = []
        
        for file_path in directory.glob('**/*'):
            if file_path.suffix.lower() in self.parsers:
                try:
                    result = self.ingest_file(str(file_path))
                    results.append(result)
                except Exception as e:
                    logger.error(f"Failed to ingest {file_path}: {e}")
                    results.append({
                        'file_path': str(file_path),
                        'success': False,
                        'error': str(e)
                    })
        
        return results
    
    def _parse_document(self, file_path: Path) -> List[Document]:
        """Parse document based on file extension."""
        suffix = file_path.suffix.lower()
        parser = self.parsers.get(suffix)
        
        if not parser:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        return parser.parse(str(file_path))
    
    def _chunk_document(self, documents: List[Document]) -> List:
        """Chunk documents into smaller pieces."""
        all_chunks = []
        for doc in documents:
            all_chunks.extend(self.chunker.split(doc))
        return all_chunks
    
    def _store_chunks(self, chunks: List) -> List[str]:
        """Store chunks in vector store."""
        return self.vector_store.add_chunks(chunks)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get pipeline statistics."""
        return {
            'vector_store': self.vector_store.get_collection_stats(),
            'embedding_cache': self.embedder.get_cache_stats(),
            'config': {
                'chunk_size': self.config.chunk_size,
                'top_k': self.config.top_k,
            }
        }
