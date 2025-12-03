import sys
import os
from pathlib import Path
import logging

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.rag.vector_store import VectorStore
from src.rag.embeddings import EmbeddingGenerator
from src.rag.models import Chunk

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    logger.info("Starting Vector Store Demo...")
    
    # 1. Initialize components
    logger.info("Initializing Embedding Generator...")
    embedding_gen = EmbeddingGenerator()
    
    logger.info("Initializing Vector Store...")
    # Use a temporary collection for demo
    vector_store = VectorStore(
        collection_name="demo_collection",
        persist_directory="data/chromadb_demo",
        embedding_function=embedding_gen
    )
    
    # Clear previous demo data
    vector_store.clear_collection()
    
    # 2. Create sample chunks
    logger.info("Creating sample chunks...")
    sample_texts = [
        "Das IFB (Institut für Freie Berufe) unterstützt Freiberufler bei der Gründung.",
        "Fördermittel können für Beratungen in Anspruch genommen werden.",
        "Die Gründung eines Unternehmens erfordert einen soliden Businessplan.",
        "Python ist eine beliebte Programmiersprache für Data Science.",
        "Der Himmel ist blau und die Sonne scheint."
    ]
    
    chunks = []
    for i, text in enumerate(sample_texts):
        chunk = Chunk(
            content=text,
            metadata={
                "source": "demo_script.py",
                "page": 1,
                "chunk_id": i,
                "category": "business" if i < 3 else "general"
            }
        )
        chunks.append(chunk)
        
    # 3. Add chunks to store
    logger.info(f"Adding {len(chunks)} chunks to vector store...")
    ids = vector_store.add_chunks(chunks)
    logger.info(f"Added chunks with IDs: {ids}")
    
    # 4. Query the store
    queries = [
        "Was macht das IFB?",
        "Wofür gibt es Geld?",
        "Programmiersprachen"
    ]
    
    logger.info("\n--- Querying Vector Store ---")
    for query in queries:
        logger.info(f"\nQuery: '{query}'")
        results = vector_store.query(query, top_k=2)
        
        for i, result in enumerate(results):
            logger.info(f"Result {i+1} (Score: {result['score']:.4f}):")
            logger.info(f"  Content: {result['content']}")
            logger.info(f"  Metadata: {result['metadata']}")

    # 5. Cleanup
    logger.info("\nDemo completed successfully.")

if __name__ == "__main__":
    main()
