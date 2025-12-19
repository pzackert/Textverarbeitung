import logging
import os
import shutil
from typing import List, Dict
from pathlib import Path
from pydantic import BaseModel

# Requires RAG pipeline integration
# For now, we mock the RAG ingestion part if pipeline isn't passed,
# or we assume we can import it. 
# Ideally, we inject dependencies.

logger = logging.getLogger(__name__)

GLOBAL_KNOWLEDGE_DIR = Path("data/global_knowledge")

class GlobalDocument(BaseModel):
    filename: str
    size_bytes: int
    
class KnowledgeService:
    def __init__(self):
        self._ensure_dir()

    def _ensure_dir(self):
        GLOBAL_KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)

    def list_documents(self) -> List[GlobalDocument]:
        docs = []
        for f in GLOBAL_KNOWLEDGE_DIR.glob("*"):
            if f.is_file():
                docs.append(GlobalDocument(filename=f.name, size_bytes=f.stat().st_size))
        return docs

    def save_file(self, filename: str, content: bytes) -> Path:
        """
        Saves file to global knowledge dir.
        Does NOT trigger RAG ingestion here (controller does that).
        """
        file_path = GLOBAL_KNOWLEDGE_DIR / filename
        with open(file_path, "wb") as f:
            f.write(content)
        return file_path

    def delete_file(self, filename: str) -> bool:
        file_path = GLOBAL_KNOWLEDGE_DIR / filename
        if file_path.exists():
            file_path.unlink()
            return True
        return False

knowledge_service = KnowledgeService()
