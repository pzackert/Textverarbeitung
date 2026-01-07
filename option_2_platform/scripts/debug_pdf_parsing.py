import time
import sys
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Mock RAGConfig if needed, but we import DoclingParser directly
try:
    from src.parsers.docling_parser import DoclingParser
except ImportError:
    logger.error("Could not import DoclingParser. Check python path.")
    sys.exit(1)

def test_pdf_parsing(file_path):
    path = Path(file_path)
    if not path.exists():
        logger.error(f"File not found: {path}")
        return

    logger.info(f"Target File: {path.name}")
    logger.info(f"Size: {path.stat().st_size / 1024 / 1024:.2f} MB")
    
    start_time = time.time()
    
    try:
        parser = DoclingParser()
        logger.info("Parser initialized. Starting parse...")
        documents = parser.parse(str(path))
        
        duration = time.time() - start_time
        logger.info(f"Parsing completed in {duration:.2f} seconds")
        
        # Analyze Output
        if not documents:
            logger.error("No documents returned!")
            return

        doc = documents[0]
        content_len = len(doc.content)
        metadata = doc.metadata
        page_count = metadata.get("page_count", "Unknown")
        
        logger.info(f"Document Content Length: {content_len} chars")
        logger.info(f"Metadata Page Count: {page_count}")
        logger.info(f"First 500 chars: {doc.content[:500]}")
        
    except Exception as e:
        logger.error(f"Parsing FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    target_file = "data/global_knowledge/the-state-of-enterprise-ai_2025-report.pdf"
    test_pdf_parsing(target_file)
