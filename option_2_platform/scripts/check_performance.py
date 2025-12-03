import time
import sys
from pathlib import Path
import logging

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.rag.embeddings import EmbeddingGenerator
from src.rag.vector_store import VectorStore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_performance():
    logger.info("Starting Performance Check...")
    
    # 1. Embedding Performance
    logger.info("Initializing EmbeddingGenerator...")
    start_init = time.time()
    embedder = EmbeddingGenerator("paraphrase-multilingual-MiniLM-L12-v2")
    logger.info(f"Model load time: {time.time() - start_init:.4f}s")

    text = "Dies ist ein Test für die Performance Messung." * 50  # ~2300 chars
    
    # Single Embedding (Uncached)
    start = time.time()
    _ = embedder.embed(text)
    duration = time.time() - start
    logger.info(f"Single embedding (uncached): {duration:.4f}s")
    
    # Single Embedding (Cached)
    start = time.time()
    _ = embedder.embed(text)
    duration_cached = time.time() - start
    logger.info(f"Single embedding (cached): {duration_cached:.4f}s")
    
    # Batch Embedding
    texts = [f"Text {i}" * 50 for i in range(10)]
    start = time.time()
    _ = embedder.embed_batch(texts)
    duration_batch = time.time() - start
    logger.info(f"Batch (10) embedding: {duration_batch:.4f}s")
    logger.info(f"Per text in batch: {duration_batch / 10:.4f}s")

    # 2. Vector Store Performance
    logger.info("Initializing VectorStore...")
    store = VectorStore(
        collection_name="perf_test",
        persist_directory="data/chromadb_perf",
        embedding_function=embedder
    )
    
    # Add data if empty
    if store.get_collection_stats()['count'] == 0:
        from src.rag.models import Chunk
        chunks = [
            Chunk(content=t, metadata={"source": "perf_test", "chunk_id": i}) 
            for i, t in enumerate(texts)
        ]
        store.add_chunks(chunks)
    
    # Query Performance
    start = time.time()
    _ = store.query("Test query", top_k=5)
    duration_query = time.time() - start
    logger.info(f"Vector Store Query time: {duration_query:.4f}s")
    
    # Cleanup
    import shutil
    shutil.rmtree("data/chromadb_perf")
    logger.info("Performance Check Complete.")

if __name__ == "__main__":
    check_performance()
