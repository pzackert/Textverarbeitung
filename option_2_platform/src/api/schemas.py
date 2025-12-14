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
    page_width: Optional[float] = None
    page_height: Optional[float] = None
    bbox: Optional[List[float]] = None  # [x0, y0, x1, y1]
    chunk_id: Optional[int] = None
    score: Optional[float] = None
    docling_id: Optional[str] = None
    table: Optional[bool] = None
    table_md: Optional[str] = None

class Citation(BaseModel):
    citation_number: int
    source: SourceInfo

class QueryRequest(BaseModel):
    question: str
    template_type: str = "standard"
    top_k: int = 5
    system_prompt: Optional[str] = None

class QueryResponse(BaseModel):
    answer: str
    sources: List[SourceInfo]
    citations: List[Citation]
    metadata: Dict[str, Any]

# --- System Schemas ---

class LLMServiceStatus(BaseModel):
    available: bool
    provider: str
    base_url: str
    can_autostart: bool = False
    instructions: Optional[str] = None

class LLMModelStatus(BaseModel):
    loaded: bool
    name: str
    size: Optional[str] = None
    can_autopull: bool = False
    instructions: Optional[str] = None

class VectorDBStatus(BaseModel):
    available: bool
    documents: int

class SystemStatus(BaseModel):
    llm_service: LLMServiceStatus
    llm_model: LLMModelStatus
    vector_db: VectorDBStatus
    # Backward compatibility
    ollama_available: bool
    chromadb_available: bool
    documents_count: int
    embeddings_cached: int = 0
