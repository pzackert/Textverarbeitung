#!/usr/bin/env python3
"""
Ingest Sample Data into ChromaDB.
"""
import sys
import os
from pathlib import Path
import logging

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.rag.ingestion import IngestionPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("ingest_samples")

def main():
    samples_dir = Path("data/samples/applications")
    if not samples_dir.exists():
        logger.error(f"Sample data directory not found: {samples_dir}")
        logger.info("Run 'python scripts/generate_sample_data.py' first.")
        sys.exit(1)
        
    logger.info("🚀 Starting Sample Data Ingestion...")
    
    pipeline = IngestionPipeline()
    
    # Walk through all subdirectories
    files_to_ingest = []
    for root, _, files in os.walk(samples_dir):
        for file in files:
            if file.lower().endswith(('.pdf', '.docx', '.xlsx')):
                files_to_ingest.append(Path(root) / file)
    
    logger.info(f"Found {len(files_to_ingest)} documents to ingest.")
    
    success_count = 0
    for file_path in files_to_ingest:
        try:
            logger.info(f"Processing: {file_path.name}")
            chunks = pipeline.ingest_file(file_path)
            logger.info(f"  ✅ Ingested {len(chunks)} chunks")
            success_count += 1
        except Exception as e:
            logger.error(f"  ❌ Failed: {e}")
            
    logger.info(f"\n✅ Ingestion Complete: {success_count}/{len(files_to_ingest)} files processed.")

if __name__ == "__main__":
    main()
