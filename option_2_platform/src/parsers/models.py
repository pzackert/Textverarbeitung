from dataclasses import dataclass, field
from typing import Dict, Any
from pathlib import Path

@dataclass
class Document:
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_file: str = ""
    file_type: str = ""
    
    def __post_init__(self):
        if not self.content or not self.content.strip():
            raise ValueError("Content cannot be empty")
        if self.file_type and self.file_type not in ["pdf", "docx", "xlsx"]:
            raise ValueError(f"Unsupported type: {self.file_type}")
    
    @property
    def filename(self) -> str:
        return Path(self.source_file).name
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "metadata": self.metadata,
            "source_file": self.source_file,
            "file_type": self.file_type,
            "filename": self.filename
        }
