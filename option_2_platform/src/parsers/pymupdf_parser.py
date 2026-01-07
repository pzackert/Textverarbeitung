import logging
from pathlib import Path
from typing import List
import fitz  # PyMuPDF
from src.parsers.models import Document, Block, BoundingBox

logger = logging.getLogger(__name__)

class PyMuPDFParser:
    """Robust PDF parser using PyMuPDF (Fitz)."""
    
    def parse(self, file_path: str) -> List[Document]:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
            
        try:
            doc = fitz.open(str(path))
            blocks: List[Block] = []
            
            for page_idx, page in enumerate(doc, start=1):
                text = page.get_text()
                if not text.strip():
                    continue
                    
                blocks.append(
                    Block(
                        text=text,
                        bbox=None,
                        page_number=page_idx,
                        block_type="page",
                        docling_id=None
                    )
                )
                
            full_text = "\n\n".join(b.text for b in blocks)
            
            # Metadata
            metadata = {
                "page_count": doc.page_count,
                "file_size": path.stat().st_size,
                "parser": "pymupdf"
            }
            
            doc.close()
            
            return [
                Document(
                    content=full_text,
                    metadata=metadata,
                    source_file=str(path),
                    file_type="pdf",
                    blocks=blocks
                )
            ]
            
        except Exception as e:
            logger.error(f"PyMuPDF parsing failed: {e}")
            raise
