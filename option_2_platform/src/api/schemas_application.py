from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
import uuid

# --- Shared Enums/Types ---

class ApplicationStatus(str):
    DRAFT = "draft"
    SUBMITTED = "submitted" # Eingereicht
    ANALYZING = "analyzing" # In Prüfung
    COMPLETED = "completed" # Abgeschlossen

# --- Document Schemas ---

class ApplicationDocument(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    size_bytes: int
    content_type: str = "application/pdf"
    uploaded_at: datetime = Field(default_factory=datetime.now)
    # Status of ingestion for this specific document
    is_indexed: bool = False
    has_annotated_version: bool = False

# Merged Criterion (Catalog + Status)
class ApplicationCriterion(BaseModel):
    id: str
    name: str
    kategorie: str
    kurz: str
    lang: str
    prompt: Optional[str] = None
    recommended: bool = False
    
    # Evaluation Status
    status: str = "open"  # open, checked, warning, failed
    manualCheck: bool = False
    score: int = 0
    reasoning: Optional[str] = None
    citations: List[Any] = []

# --- Application Models ---

class ApplicationBase(BaseModel):
    title: str = Field(..., description="Projektname / Titel")
    applicant: str = Field(..., description="Antragsteller")
    description: Optional[str] = None
    funding_request: Optional[float] = None
    
class ApplicationCreate(ApplicationBase):
    pass

class ApplicationUpdate(BaseModel):
    title: Optional[str] = None
    applicant: Optional[str] = None
    description: Optional[str] = None
    funding_request: Optional[float] = None
    status: Optional[str] = None
    rag_status: Optional[str] = None # Added for update_application usage

class Application(ApplicationBase):
    id: str
    status: str = "draft"
    created_at: datetime
    updated_at: datetime
    documents: List[ApplicationDocument] = []
    
    # Validation/Rag State (Simplified for list view)
    rag_status: str = "pending" # "pending", "indexing", "ready", "empty"

class ApplicationSummary(BaseModel):
    id: str
    title: str
    applicant: str
    status: str
    created_at: datetime
    updated_at: datetime
    document_count: int
