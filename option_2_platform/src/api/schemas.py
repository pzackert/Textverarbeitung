from typing import List, Optional, Dict, Any
from pydantic import BaseModel

# --- Ingestion Schemas ---

class IngestResponse(BaseModel):
    success: bool
    file_path: str
    chunks_count: int
    message: str

# --- Query Schemas ---

class SourceInfo(BaseModel):
    source_file: str
    page_number: Optional[int] = None
    chunk_id: Optional[int] = None
    score: Optional[float] = None

class Citation(BaseModel):
    citation_number: int
    source: SourceInfo

class QueryRequest(BaseModel):
    question: str
    template_type: str = "standard"
    top_k: int = 5

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    citations: List[Citation]
    metadata: Dict[str, Any]

# --- System Schemas ---

class SystemStatus(BaseModel):
    ollama_available: bool
    chromadb_available: bool
    documents_count: int
    embeddings_cached: int
