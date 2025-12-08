import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class PDFAnnotationService:
    """
    Service for creating annotated copies of PDFs with highlighted citations.
    Uses PyMuPDF (fitz) for high-performance PDF manipulation.
    """
    
    def create_annotated_pdf(self, input_path: Path, output_path: Path, citations: List[Dict[str, Any]]) -> bool:
        """
        Create a copy of the PDF with highlights for all citations.
        
        Args:
            input_path: Path to original PDF
            output_path: Path where annotated PDF should be saved
            citations: List of citation objects (must contain 'page' and 'quote' or 'text_segment')
            
        Returns:
            bool: True if successful
        """
        try:
            doc = fitz.open(input_path)
            
            for citation in citations:
                self._highlight_citation(doc, citation)
                
            doc.save(output_path)
            doc.close()
            return True
            
        except Exception as e:
            logger.error(f"Failed to annotate PDF {input_path}: {str(e)}")
            return False

    def _highlight_citation(self, doc, citation: Dict[str, Any]):
        """Apply highlight to a single citation."""
        try:
            # Get page number (0-based in fitz, usually 1-based in data)
            page_num = citation.get('page', 1) - 1
            if page_num < 0 or page_num >= len(doc):
                return

            page = doc[page_num]
            text_to_find = citation.get('quote') or citation.get('text_segment')
            
            if not text_to_find:
                return

            # Search for text instances
            # quad=True returns quadrilaterals which is better for multi-line text
            text_instances = page.search_for(text_to_find, quads=True)
            
            # Add highlight annotation for each instance found
            for quad in text_instances:
                annot = page.add_highlight_annot(quad)
                annot.set_colors(stroke=(1, 1, 0))  # Yellow
                annot.set_opacity(0.5)
                annot.update()
                
        except Exception as e:
            logger.warning(f"Could not highlight citation on page {citation.get('page')}: {e}")
