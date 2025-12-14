from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from pathlib import Path


@dataclass
class BoundingBox:
    """Bounding box in PDF coordinate space (Docling origin: top-left)."""
    page: int
    x0: float
    y0: float
    x1: float
    y1: float
    page_width: float
    page_height: float


@dataclass
class Block:
    """Semantic block emitted by Docling."""
    text: str
    bbox: Optional[BoundingBox]
    block_type: str = "paragraph"  # paragraph | table | list | heading
    table_md: Optional[str] = None
    docling_id: Optional[str] = None
    page_number: Optional[int] = None


@dataclass
class Document:
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    source_file: str = ""
    file_type: str = ""
    blocks: List[Block] = field(default_factory=list)

    def __post_init__(self):
        if not self.content or not self.content.strip():
            raise ValueError("Content cannot be empty")
        # Accept any file type now; validation happens in parser

    @property
    def filename(self) -> str:
        return Path(self.source_file).name

    def to_dict(self) -> Dict[str, Any]:
        return {
            "content": self.content,
            "metadata": self.metadata,
            "source_file": self.source_file,
            "file_type": self.file_type,
            "filename": self.filename,
        }
