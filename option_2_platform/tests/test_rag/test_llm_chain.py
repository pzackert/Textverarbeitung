import pytest
from unittest.mock import Mock, MagicMock, patch
from src.rag.llm_chain import LLMChain, create_llm_chain
from src.rag.config import RAGConfig
from src.rag.response_parser import ResponseParser

class TestResponseParser:
    
    def test_citation_extraction_regex(self):
        parser = ResponseParser()
        text = "This is a fact [Quelle 1]. Another fact [Quelle 2, 3]."
        citations = parser.extract_citations(text)
        assert citations == {1, 2, 3}
        
    def test_citation_extraction_variations(self):
        parser = ResponseParser()
        text = "[Quelle 1] [Quelle 1,2] [Quelle  3 ]"
        citations = parser.extract_citations(text)
        assert citations == {1, 2, 3}
        
    def test_map_citations(self):
        parser = ResponseParser()
        sources = [
            {"metadata": {"source": "doc1.pdf", "page": 1}},
            {"metadata": {"source": "doc2.pdf", "page": 5}}
        ]
        
        mapped = parser.map_citations({1, 2}, sources)
        assert len(mapped) == 2
        assert mapped[0]["source"] == "doc1.pdf"
        assert mapped[0]["number"] == 1
        assert mapped[1]["source"] == "doc2.pdf"
        assert mapped[1]["number"] == 2
        
    def test_map_citations_out_of_range(self):
        parser = ResponseParser()
        sources = [{"metadata": {"source": "doc1.pdf"}}]
        mapped = parser.map_citations({1, 99}, sources)
        assert len(mapped) == 1
        assert mapped[0]["number"] == 1

class TestLLMChain:
    
    @pytest.fixture
    def mock_components(self):
        retrieval = MagicMock()
        llm = MagicMock()
        prompt_builder = MagicMock()
        config = RAGConfig()
        return retrieval, llm, prompt_builder, config
        
    def test_llm_chain_initialization(self, mock_components):
        retrieval, llm, prompt_builder, config = mock_components
        chain = LLMChain(retrieval, llm, prompt_builder, config)
        assert chain.retrieval_engine == retrieval
        assert chain.llm_provider == llm
        
    def test_query_execution_with_mock(self, mock_components):
        retrieval, llm, prompt_builder, config = mock_components
        chain = LLMChain(retrieval, llm, prompt_builder, config)
        
        # Setup mocks
        retrieval.retrieve.return_value = [{"content": "test", "metadata": {"source": "doc.pdf"}}]
        prompt_builder.build_query_prompt.return_value = "Prompt"
        llm.generate.return_value = "Answer [Quelle 1]"
        llm.model_name = "test-model"
        
        # Execute
        result = chain.query("Question")
        
        # Verify
        assert result["answer"] == "Answer [Quelle 1]"
        assert len(result["citations"]) == 1
        assert result["citations"][0]["source"] == "doc.pdf"
        assert result["metadata"]["chunks_retrieved"] == 1
        
        # Verify calls
        retrieval.retrieve.assert_called_once()
        prompt_builder.build_query_prompt.assert_called_once()
        llm.generate.assert_called_once()
        
    def test_error_handling_no_results(self, mock_components):
        retrieval, llm, prompt_builder, config = mock_components
        chain = LLMChain(retrieval, llm, prompt_builder, config)
        
        retrieval.retrieve.return_value = []
        
        result = chain.query("Question")
        assert "keine relevanten Informationen" in result["answer"]
        assert len(result["sources"]) == 0
        llm.generate.assert_not_called()
        
    def test_error_handling_llm_unavailable(self, mock_components):
        retrieval, llm, prompt_builder, config = mock_components
        chain = LLMChain(retrieval, llm, prompt_builder, config)
        
        retrieval.retrieve.return_value = [{"content": "test"}]
        llm.generate.side_effect = ConnectionError("Offline")
        
        with pytest.raises(ConnectionError):
            chain.query("Question")

    @patch('src.rag.llm_chain.RAGConfig')
    @patch('src.rag.llm_chain.EmbeddingGenerator')
    @patch('src.rag.llm_chain.VectorStore')
    @patch('src.rag.llm_chain.RetrievalEngine')
    @patch('src.rag.llm_chain.OllamaProvider')
    @patch('src.rag.llm_chain.PromptBuilder')
    def test_factory_function(self, mock_pb, mock_op, mock_re, mock_vs, mock_eg, mock_conf):
        # Setup mocks for factory
        mock_op_instance = Mock()
        mock_op_instance.test_connection.return_value = {"available": True, "model_info": "Test"}
        mock_op.return_value = mock_op_instance
        
        chain = create_llm_chain()
        assert isinstance(chain, LLMChain)
        mock_op.assert_called_once()
