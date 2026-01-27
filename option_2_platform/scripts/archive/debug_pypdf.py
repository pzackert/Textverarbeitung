import logging
from pathlib import Path
import fitz  # PyMuPDF

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pymupdf(file_path):
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {path}")
        return

    logger.info(f"Target File: {path.name}")
    try:
        doc = fitz.open(str(path))
        num_pages = doc.page_count
        logger.info(f"PyMuPDF Page Count: {num_pages}")
        
        text_content = ""
        for page in doc:
            text = page.get_text()
            if text:
                text_content += text + "\n"
                
        logger.info(f"Total Text Length: {len(text_content)} chars")
        logger.info(f"First 500 chars: {text_content[:500]}")
        doc.close()
        
    except Exception as e:
        logger.error(f"PyMuPDF Failed: {e}")

if __name__ == "__main__":
    target_file = "data/global_knowledge/the-state-of-enterprise-ai_2025-report.pdf"
    test_pymupdf(target_file)
