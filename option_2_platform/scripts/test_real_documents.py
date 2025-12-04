#!/usr/bin/env python3
import sys
import os
import time
import logging
from pathlib import Path
import asyncio

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.rag.ingestion import IngestionPipeline
from src.services.project_service import project_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("test_real_documents")

async def main():
    test_dir = Path("data/test_documents")
    if not test_dir.exists():
        logger.error(f"Test directory not found: {test_dir}")
        return

    documents = list(test_dir.glob("*"))
    logger.info(f"Found {len(documents)} documents in {test_dir}")

    # Create a test project
    project = project_service.create_project(
        name="Real Test Documents",
        description="Integration test with real documents from option_1"
    )
    logger.info(f"Created project: {project.name} ({project.id})")

    pipeline = IngestionPipeline()
    
    stats = {
        "total": len(documents),
        "success": 0,
        "failed": 0,
        "chunks": 0,
        "start_time": time.time()
    }

    print("\nTEST DOCUMENT PROCESSING REPORT")
    print("===============================")

    for doc_path in documents:
        if doc_path.name.startswith("."):
            continue
            
        print(f"\nDocument: {doc_path.name}")
        start_time = time.time()
        
        try:
            # 1. Save to project
            with open(doc_path, "rb") as f:
                content = f.read()
            
            saved_doc = project_service.save_document(project.id, doc_path.name, content)
            if not saved_doc:
                raise Exception("Failed to save document to project")
            logger.info(f"Saved to project: {saved_doc.path}")

            # 2. Ingest
            result = pipeline.ingest_file(str(saved_doc.path))
            chunks_count = result.get("chunk_count", 0)
            
            duration = time.time() - start_time
            print(f"✅ Processing: {chunks_count} chunks, {duration:.1f}s")
            
            stats["success"] += 1
            stats["chunks"] += chunks_count
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            stats["failed"] += 1

    total_time = time.time() - stats["start_time"]
    
    print("\nSummary:")
    print(f"- Total: {stats['total']}")
    print(f"- Success: {stats['success']}")
    print(f"- Failed: {stats['failed']}")
    print(f"- Total Chunks: {stats['chunks']}")
    print(f"- Total Time: {total_time:.1f}s")
    
    if stats["failed"] == 0:
        print("\n✅ ALL TESTS PASSED")
    else:
        print("\n⚠️  SOME TESTS FAILED")

if __name__ == "__main__":
    asyncio.run(main())
