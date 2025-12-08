from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import random
import string

def generate_short_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    path: str
    size: Optional[int] = 0
    uploaded_at: datetime = Field(default_factory=datetime.now)

class Project(BaseModel):
    id: str = Field(default_factory=generate_short_id)
    name: str
    description: Optional[str] = None
    applicant: Optional[str] = None
    funding_amount: Optional[float] = None
    status: str = "draft"  # draft, in_review, completed
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    documents: List[Document] = Field(default_factory=list)
    
    # Validation Results
    validation_results: Optional[Dict[str, Any]] = None
    annotated_documents: Optional[Dict[str, str]] = None
    
    # Computed fields for UI
    doc_count: int = 0
    status_display: str = ""
    last_updated: str = ""
