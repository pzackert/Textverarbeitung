from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import uuid

class Document(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    filename: str
    path: str
    uploaded_at: datetime = Field(default_factory=datetime.now)

class Project(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    documents: List[Document] = Field(default_factory=list)
