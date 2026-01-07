
import sys
from pathlib import Path
from src.rag.ingestion import IngestionPipeline

def debug_herbert():
    path = Path("data/global_knowledge/Herbert.txt")
    if not path.exists():
        print(f"[ERROR] {path} does not exist.")
        return

    print(f"Ingesting {path}...")
    pipeline = IngestionPipeline()
    try:
        result = pipeline.ingest_file(
            str(path),
            project_id=None,
            extra_metadata={"type": "global_knowledge", "document": path.name}
        )
        print("Ingestion Result:")
        print(result)
        
        # Verify chunks count
        if result['chunk_count'] == 0:
            print("[FAIL] 0 Chunks created for Herbert.txt!")
            # Check content
            print(f"File content ({path.stat().st_size} bytes):")
            print(path.read_text())
        else:
             print("[PASS] Chunks created.")
             
    except Exception as e:
        print(f"[ERROR] Ingestion crashed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_herbert()
