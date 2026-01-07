"""
Document Ingestion Pipeline Service.
Orchestrates: Document → Parser → Chunker → Embeddings → Vector Store
"""
from pathlib import Path
from typing import List, Optional, Dict, Any
import logging

from src.parsers.docling_parser import DoclingParser
from src.parsers.csv_parser import CSVParser
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
    
    def __init__(self, config: Optional[RAGConfig] = None, vector_store: Optional[VectorStore] = None):
        """
        Initialize ingestion pipeline with configuration.
        
        Args:
            config: RAG configuration (uses default if None)
            vector_store: Optional shared VectorStore instance
        """
        self.config = config or RAGConfig.from_yaml()
        
        # Initialize components
        self._init_parsers()
        self._init_chunker()
        self._init_embedder()
        
        if vector_store:
            self.vector_store = vector_store
        else:
            self._init_vector_store()
    
    def _init_parsers(self):
        """Initialize document parsers."""
        self.parsers = {
            '.pdf': DoclingParser(),
            '.docx': DoclingParser(),
            '.xlsx': DoclingParser(),
            '.csv': CSVParser(),
        }
        # Text files are handled inline in ingest_file, but we keep them in the map
        # so directory ingestion can pick them up.
        self.parsers['.txt'] = None
    
    def _init_chunker(self):
        """Initialize chunker with config."""
        self.chunker = Chunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            max_tokens=self.config.max_chunk_tokens,
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
            embedding_function=self.embedder,
            schema_version=self.config.metadata_schema_version,
        )
        self.vector_store.ensure_schema(self.config.metadata_schema_version)
    
    def ingest_file(
        self,
        file_path: str,
        project_id: Optional[str] = None,
        extra_metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Ingest a single file through complete pipeline.
        
        Args:
            file_path: Path to document file
            project_id: Optional project ID to associate with chunks
            
        Returns:
            Ingestion results with statistics
        """
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        # 1. Parse document (support lightweight TXT ingestion)
        if path.suffix.lower() == ".txt":
            text_content = path.read_text(encoding="utf-8")
            documents = [
                Document(
                    content=text_content,
                    metadata={"page_count": 1, "page_number": 1},
                    source_file=str(path),
                    file_type="txt",
                    blocks=[],
                )
            ]
        else:
            documents = self._parse_document(path)
        
        # 2. Chunk document
        chunks = self._chunk_document(documents)
        
        # Add extra metadata
        for chunk in chunks:
            if project_id:
                chunk.metadata["project_id"] = project_id
            
            chunk.metadata["doc_id"] = path.stem
            chunk.metadata["doc_name"] = path.name
            if extra_metadata:
                chunk.metadata.update(extra_metadata)
            # Ensure page_number is present (PDFParser adds it)
            # If not present (e.g. other parsers), default to 1
            if "page_number" not in chunk.metadata:
                chunk.metadata["page_number"] = 1
            
            # Ensure 'source' key is present for VectorStore and Citations
            if "source" not in chunk.metadata:
                chunk.metadata["source"] = path.name
        
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
            suffix = file_path.suffix.lower()
            if suffix in self.parsers or suffix == '.txt':
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

        if suffix == '.txt':  # handled earlier, guard for safety
            raise ValueError("TXT parsing should be handled before _parse_document")

        if not parser:
            raise ValueError(f"Unsupported file type: {suffix}")
        
        # Try primary parser (Docling)
        try:
            documents = parser.parse(str(file_path))
            # Heuristic validation: If PDF is > 10KB but we got < 200 chars, it likely failed/OCRed poorly
            is_pdf = suffix == ".pdf"
            if is_pdf and file_path.stat().st_size > 10000:
                total_text = sum(len(d.content) for d in documents)
                if total_text < 200:
                    logger.warning(f"Docling returned only {total_text} chars for {file_path.name}. Falling back to PyMuPDF.")
                    raise ValueError("Insufficient content from Docling")
            return documents
            
        except Exception as e:
            if suffix == ".pdf":
                logger.warning(f"Primary parser failed for {file_path.name}: {e}. Trying fallback (PyMuPDF)...")
                try:
                    from src.parsers.pymupdf_parser import PyMuPDFParser
                    fallback_parser = PyMuPDFParser()
                    return fallback_parser.parse(str(file_path))
                except Exception as fallback_error:
                    logger.error(f"Fallback parser also failed: {fallback_error}")
                    raise e # Raise original logic error if both fail
            raise e
    
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
