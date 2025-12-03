import pytest
from unittest.mock import Mock, MagicMock
from src.rag.prompts import PromptTemplate, format_context
from src.rag.prompt_builder import PromptBuilder
from src.rag.retrieval import RetrievalEngine

class TestPromptTemplate:
    
    def test_initialization(self):
        template = PromptTemplate("System", "User {query}")
        assert template.system_prompt == "System"
        assert template.user_template == "User {query}"
        
    def test_formatting(self):
        template = PromptTemplate("System", "Context: {context} Query: {query}")
        result = template.format(query="Test?", context="Content")
        assert "System" in result
        assert "Context: Content" in result
        assert "Query: Test?" in result
        
    def test_factory_methods(self):
        t1 = PromptTemplate.standard_query()
        assert "IFB-Förderrichtlinien" in t1.system_prompt
        assert "Frage" in t1.user_template
        
        t2 = PromptTemplate.criteria_evaluation()
        assert "Prüfer" in t2.system_prompt
        assert "Kriterium" in t2.user_template
        
        t3 = PromptTemplate.document_summary()
        assert "fasse" in t3.user_template

class TestContextFormatting:
    
    def test_format_context_basic(self):
        results = [
            {"content": "Chunk 1", "metadata": {"source": "doc1.pdf", "page": 1}},
            {"content": "Chunk 2", "metadata": {"source": "doc2.pdf"}}
        ]
        formatted = format_context(results)
        assert "[Quelle 1: doc1.pdf, Seite 1]" in formatted
        assert "Chunk 1" in formatted
        assert "[Quelle 2: doc2.pdf]" in formatted
        assert "Chunk 2" in formatted
        
    def test_format_context_empty(self):
        assert format_context([]) == ""

class TestPromptBuilder:
    
    @pytest.fixture
    def mock_engine(self):
        engine = MagicMock(spec=RetrievalEngine)
        engine.retrieve.return_value = [
            {"content": "Test Content", "metadata": {"source": "test.pdf"}}
        ]
        return engine
        
    def test_builder_initialization(self, mock_engine):
        builder = PromptBuilder(mock_engine)
        assert builder.retrieval_engine == mock_engine
        
    def test_build_standard_prompt(self, mock_engine):
        builder = PromptBuilder(mock_engine)
        prompt = builder.build_query_prompt("Test Query", "standard")
        
        assert "IFB-Förderrichtlinien" in prompt
        assert "Test Query" in prompt
        assert "Test Content" in prompt
        assert "[Quelle 1: test.pdf]" in prompt
        
    def test_build_evaluation_prompt(self, mock_engine):
        builder = PromptBuilder(mock_engine)
        prompt = builder.build_query_prompt("Test Criteria", "evaluation")
        
        assert "Prüfer" in prompt
        assert "Test Criteria" in prompt
        assert "Bewertung:" in prompt
        
    def test_build_unknown_template(self, mock_engine):
        builder = PromptBuilder(mock_engine)
        prompt = builder.build_query_prompt("Query", "unknown_type")
        # Should fallback to standard
        assert "IFB-Förderrichtlinien" in prompt
        
    def test_german_language(self, mock_engine):
        builder = PromptBuilder(mock_engine)
        prompt = builder.build_query_prompt("Query")
        
        assert "Frage" in prompt
        assert "Kontext" in prompt
        assert "Quelle" in prompt
