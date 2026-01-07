
import sys
import os
from unittest.mock import MagicMock
from src.rag.llm_chain import LLMChain
from src.rag.retrieval import RetrievalEngine
from src.rag.exceptions import RAGException

# Mock RetrievalEngine to simulate failure
mock_retrieval = MagicMock(spec=RetrievalEngine)
mock_retrieval.retrieve.side_effect = RAGException("Simulated VectorStore Failure")

# Mock other components
mock_llm = MagicMock()
mock_prompt = MagicMock()
mock_config = MagicMock()
mock_config.top_k = 5

def test_crash():
    chain = LLMChain(
        retrieval_engine=mock_retrieval,
        llm_provider=mock_llm,
        prompt_builder=mock_prompt,
        config=mock_config
    )
    
    print("Attempting query with broken retrieval...")
    try:
        chain.query("Hello")
        print("SUCCESS: Handling graceful failure.")
    except Exception as e:
        print(f"CRASH: Caught {type(e).__name__}: {e}")

if __name__ == "__main__":
    test_crash()
