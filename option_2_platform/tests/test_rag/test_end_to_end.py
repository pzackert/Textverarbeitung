import pytest
import requests
from src.rag.llm_chain import create_llm_chain

def is_ollama_available():
    try:
        response = requests.get("http://localhost:11434", timeout=1)
        return response.status_code == 200
    except:
        return False

@pytest.mark.integration
class TestEndToEnd:
    
    @pytest.fixture(scope="class")
    def chain(self):
        return create_llm_chain()

    @pytest.mark.skipif(not is_ollama_available(), reason="Ollama not running")
    def test_complete_rag_pipeline(self, chain):
        """
        Test complete RAG pipeline end-to-end with real LLM.
        """
        query = "Was sind die Fördervoraussetzungen?"
        
        # Execute query
        result = chain.query(query)
        
        # Verify structure
        assert "answer" in result
        assert "citations" in result
        assert "sources" in result
        assert "metadata" in result
        
        # Verify content (assuming we ingested relevant docs)
        # We ingested 'Dokument.pdf' and 'Förderantrag.docx'
        # If they contain relevant info, we should get citations.
        # Since these are dummy docs from 'A_Perfekter Fall', they might contain generic text.
        # But we check if we got an answer that is not empty.
        assert len(result["answer"]) > 10
        
        # Check metadata
        assert result["metadata"]["chunks_retrieved"] > 0
        assert result["metadata"]["duration"] > 0

    def test_retrieval_only(self, chain):
        """
        Test retrieval part only (always runs).
        """
        query = "Förderung"
        results = chain.retrieval_engine.retrieve(query, top_k=3)
        
        assert len(results) > 0
        assert "content" in results[0]
        assert "metadata" in results[0]
