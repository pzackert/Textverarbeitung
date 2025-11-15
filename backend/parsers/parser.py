"""Document Parser - Vereinheitlichte Schnittstelle"""
from pathlib import Path
from typing import Dict, Any
from backend.parsers.pdf_parser import PDFParser
from backend.parsers.docx_parser import DOCXParser
from backend.parsers.xlsx_parser import XLSXParser
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

PARSERS = {
    '.pdf': PDFParser(),
    '.docx': DOCXParser(),
    '.xlsx': XLSXParser()
}


def parse_document(file_path: Path) -> Dict[str, Any]:
    """Parse Dokument automatisch basierend auf Extension"""
    if not file_path.exists():
        return {"text": "", "metadata": {}, "error": "Datei nicht gefunden"}
    
    ext = file_path.suffix.lower()
    parser = PARSERS.get(ext)
    
    if not parser:
        return {"text": "", "metadata": {}, "error": f"Nicht unterstütztes Format: {ext}"}
    
    return parser.parse(file_path)
