import time
import sys
from pathlib import Path
import logging

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.rag.llm_chain import create_llm_chain
from src.rag.ingestion import IngestionPipeline
from src.rag.config import RAGConfig

logging.basicConfig(level=logging.ERROR)

def benchmark_component(name, func, iterations=1):
    start = time.time()
    for _ in range(iterations):
        func()
    duration = (time.time() - start) / iterations
    print(f"{name:<20}: {duration:.4f}s")
    return duration

def main():
    print("Performance Benchmark")
    print("=" * 50)
    
    try:
        chain = create_llm_chain()
        config = RAGConfig.from_yaml()
        pipeline = IngestionPipeline(config)
    except Exception as e:
        print(f"Setup failed: {e}")
        return

    # 1. Embedding Performance
    print("\n1. Embedding Performance")
    text = "This is a test sentence for embedding generation benchmark."
    
    def run_embedding():
        chain.retrieval_engine.vector_store.embedding_function.embed(text)
        
    benchmark_component("Embedding (cached)", run_embedding, iterations=100)
    
    # Force no cache (if possible) or just new text
    def run_embedding_new():
        chain.retrieval_engine.vector_store.embedding_function.embed(f"New text {time.time()}")
        
    benchmark_component("Embedding (new)", run_embedding_new, iterations=10)

    # 2. Retrieval Performance
    print("\n2. Retrieval Performance")
    def run_retrieval():
        chain.retrieval_engine.retrieve("Förderung", top_k=5)
        
    benchmark_component("Vector Search", run_retrieval, iterations=20)

    # 3. Full Pipeline (if Ollama available)
    if chain.llm_provider.is_available():
        print("\n3. Full Pipeline Performance")
        def run_query():
            chain.query("Was ist Förderung?")
        
        benchmark_component("End-to-End Query", run_query, iterations=3)
    else:
        print("\n3. Full Pipeline: Skipped (Ollama not available)")

if __name__ == "__main__":
    main()
