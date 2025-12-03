import sys
import time
import logging
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.rag.ingestion import IngestionPipeline
from src.rag.config import RAGConfig

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logging.getLogger("chromadb").setLevel(logging.WARNING)

def main():
    print("Ingesting Test Documents")
    print("=" * 50)
    
    # 1. Setup
    docs_dir = Path("data/test_docs")
    if not docs_dir.exists():
        print(f"❌ Directory {docs_dir} not found.")
        return
        
    files = list(docs_dir.glob("*.*"))
    print(f"Found {len(files)} documents:")
    for f in files:
        print(f"- {f.name}")
        
    # 2. Initialize Pipeline
    try:
        config = RAGConfig.from_yaml()
        # Use a separate collection for testing if needed, but for now we use the default
        # config.collection_name = "test_collection" 
        pipeline = IngestionPipeline(config)
    except Exception as e:
        print(f"❌ Pipeline initialization failed: {e}")
        return
        
    # 3. Run Ingestion
    print("\nStarting ingestion...")
    start_time = time.time()
    
    try:
        # Ingest directory
        stats_list = pipeline.ingest_directory(str(docs_dir))
        
        duration = time.time() - start_time
        print(f"\n✅ Ingestion complete in {duration:.2f}s")
        
        # Aggregate stats
        total_chunks = sum(s.get('chunks', 0) for s in stats_list)
        print(f"Chunks created: {total_chunks}")
        print(f"Documents processed: {len(stats_list)}")
        
    except Exception as e:
        print(f"❌ Ingestion failed: {e}")

if __name__ == "__main__":
    main()
