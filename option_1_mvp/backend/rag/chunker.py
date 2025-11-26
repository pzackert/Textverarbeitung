"""Text Chunking mit Overlap"""
from typing import List
from backend.utils.config import get_config_value
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


def chunk_text(text: str, chunk_size: int = 0, chunk_overlap: int = 0) -> List[str]:
    """Split Text in Chunks mit Overlap"""
    if chunk_size == 0:
        chunk_size = get_config_value('rag.chunk_size', 500)
    if chunk_overlap == 0:
        chunk_overlap = get_config_value('rag.chunk_overlap', 50)
    
    if not text:
        return []
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        
        if chunk:
            chunks.append(chunk)
        
        start = end - chunk_overlap if chunk_overlap < chunk_size else end
    
    logger.info(f"Text in {len(chunks)} Chunks aufgeteilt (Größe={chunk_size}, Overlap={chunk_overlap})")
    return chunks

