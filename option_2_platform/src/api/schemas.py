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

class ComponentStatus(BaseModel):
    status: str  # "loading" | "ready" | "error" | "pending" | "connecting"
    progress: int = 0
    message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None

class SystemComponents(BaseModel):
    ollama: ComponentStatus
    lm_studio: ComponentStatus
    llm_model: ComponentStatus
    embedding_model: ComponentStatus
    chromadb: ComponentStatus
    rag_pipeline: ComponentStatus

class SystemStatus(BaseModel):
    status: str  # "initializing" | "ready" | "error"
    components: SystemComponents
    # Backward compatibility (Optional)
    ollama_available: bool = False
    chromadb_available: bool = False
    documents_count: int = 0
    embeddings_cached: int = 0
