import logging
import sys
from pathlib import Path

# Fix path to allow imports from src
sys.path.append(str(Path.cwd()))

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from src.rag.ingestion import IngestionPipeline

def debug_ingest():
    target_file = "data/global_knowledge/the-state-of-enterprise-ai_2025-report.pdf"
    logger.info(f"Target: {target_file}")
    
    pipeline = IngestionPipeline()
    try:
        result = pipeline.ingest_file(target_file)
        logger.info(f"Ingestion Result: {result}")
    except Exception as e:
        logger.error(f"Ingestion FAILED: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_ingest()
