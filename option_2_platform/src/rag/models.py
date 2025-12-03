from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class Chunk(BaseModel):
    """
    Represents a semantic chunk of text from a document.
    """
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    embedding: Optional[List[float]] = None

    def to_chroma_payload(self) -> Dict[str, Any]:
        """
        Prepares the chunk for ChromaDB ingestion.
        """
        return {
            "document": self.content,
            "metadata": self.metadata,
            "id": f"{self.metadata.get('source', 'unknown')}_{self.metadata.get('chunk_id', '0')}"
        }
