import fitz  # PyMuPDF
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PDFAnnotationService:
    """
    Service for creating annotated copies of PDFs with highlighted citations.
    Uses PyMuPDF (fitz) for high-performance PDF manipulation.
    """
    
    # Color definitions for different statuses
    COLORS = {
        'success': (0, 1, 0),      # Green
        'pass': (0, 1, 0),          # Green
        'warning': (1, 1, 0),       # Yellow
        'fail': (1, 0, 0),          # Red
        'default': (1, 1, 0)        # Yellow (default)
    }
    
    def create_annotated_pdf(
        self, 
        input_path: Path, 
        output_path: Path, 
        citations: List[Dict[str, Any]],
        status: str = 'default'
    ) -> bool:
        """
        Create a copy of the PDF with highlights for all citations.
        
        Args:
            input_path: Path to original PDF
            output_path: Path where annotated PDF should be saved
            citations: List of citation objects (must contain 'page' and 'quote' or 'text_segment')
            status: Status for color coding ('success'/'pass', 'warning', 'fail')
            
        Returns:
            bool: True if successful
        """
        try:
            if not input_path.exists():
                logger.error(f"Input PDF not found: {input_path}")
                return False
            
            # Open PDF
            doc = fitz.open(input_path)
            
            # Get color based on status
            color = self.COLORS.get(status.lower(), self.COLORS['default'])
            
            # Apply highlights
            for citation in citations:
                self._highlight_citation(doc, citation, color)
                
            # Ensure output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save annotated PDF
            doc.save(output_path)
            doc.close()
            
            logger.info(f"Successfully created annotated PDF: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to annotate PDF {input_path}: {str(e)}")
            return False

    def _highlight_citation(self, doc, citation: Dict[str, Any], color: tuple):
        """Apply highlight to a single citation."""
        try:
            # Get page number (0-based in fitz, usually 1-based in data)
            page_num = citation.get('page', 1) - 1
            if page_num < 0 or page_num >= len(doc):
                logger.warning(f"Page {page_num + 1} out of range for document")
                return

            page = doc[page_num]
            text_to_find = citation.get('quote') or citation.get('text_segment') or citation.get('text')
            
            if not text_to_find:
                logger.warning("No text found in citation to highlight")
                return

            # Search for text instances
            # quads=True returns quadrilaterals which is better for multi-line text
            text_instances = page.search_for(text_to_find, quads=True)
            
            if not text_instances:
                # Try with first 100 characters if full text not found
                text_to_find_short = text_to_find[:100]
                text_instances = page.search_for(text_to_find_short, quads=True)
            
            # Add highlight annotation for each instance found
            for quad in text_instances:
                annot = page.add_highlight_annot(quad)
                annot.set_colors(stroke=color)  # Use specified color
                annot.set_opacity(0.4)
                annot.update()
                
            if text_instances:
                logger.debug(f"Highlighted {len(text_instances)} instance(s) on page {page_num + 1}")
                
        except Exception as e:
            logger.warning(f"Could not highlight citation on page {citation.get('page')}: {e}")
    
    def annotate_from_rag_results(
        self,
        project_id: str,
        original_filename: str,
        rag_sources: List[Dict[str, Any]],
        status: str = 'default'
    ) -> Optional[str]:
        """
        Create an annotated PDF from RAG retrieval results.
        
        Args:
            project_id: The project ID
            original_filename: Name of original PDF file
            rag_sources: List of RAG source dictionaries with 'page' and 'text' or 'content'
            status: Evaluation status for color coding
            
        Returns:
            Filename of annotated PDF if successful, None otherwise
        """
        try:
            # Determine input path - Unified structure
            base_input = Path("data/input") / project_id / "uploads"
            
            input_path = None
            if (base_input / original_filename).exists():
                input_path = base_input / original_filename
            
            if not input_path:
                logger.error(f"Original file not found: {original_filename}")
                return None
            
            # Generate output filename with _annotated suffix
            name_parts = original_filename.rsplit('.', 1)
            if len(name_parts) == 2:
                annotated_filename = f"{name_parts[0]}_annotated.{name_parts[1]}"
            else:
                annotated_filename = f"{original_filename}_annotated"
            
            # Output path
            output_dir = Path("data/input") / project_id / "annotated"
            output_path = output_dir / annotated_filename
            
            # Convert RAG sources to citation format
            citations = []
            for source in rag_sources:
                citations.append({
                    'page': source.get('page', 1),
                    'text': source.get('text') or source.get('content') or source.get('page_content', '')
                })
            
            # Create annotated PDF
            success = self.create_annotated_pdf(input_path, output_path, citations, status)
            
            return annotated_filename if success else None
            
        except Exception as e:
            logger.error(f"Failed to create annotated PDF from RAG results: {e}")
            return None


# Singleton instance
pdf_annotation_service = PDFAnnotationService()
