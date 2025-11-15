"""Test: Criteria Engine"""
import pytest
from backend.core.criteria import check_criterion, check_all_criteria, CRITERIA
from backend.llm.lm_studio_client import LMStudioClient
from backend.rag.vector_store import VectorStore
from backend.rag.chunker import chunk_text


@pytest.mark.integration
def test_criteria_structure():
    """Test Criteria Definitionen"""
    assert len(CRITERIA) == 6
    
    for criterion in CRITERIA:
        assert "id" in criterion
        assert "name" in criterion
        assert "prompt" in criterion


@pytest.mark.integration
def test_single_criterion_check():
    """Test einzelnes Kriterium"""
    llm = LMStudioClient()
    store = VectorStore()
    store.clear_all()
    
    # Sample document
    doc_text = "Das Unternehmen TechInnovate GmbH hat seinen Sitz in Erfurt, Thüringen."
    chunks = chunk_text(doc_text, chunk_size=100, chunk_overlap=20)
    store.add_documents(
        chunks,
        [{"doc": "test", "chunk": i} for i in range(len(chunks))],
        [f"test_{i}" for i in range(len(chunks))]
    )
    
    # Check company_location criterion
    result = check_criterion("company_location", doc_text, llm, store)
    
    assert result["id"] == "company_location"
    assert result["result"] in ["PASSED", "FAILED", "UNCLEAR"]
    assert "answer" in result


@pytest.mark.integration
def test_all_criteria():
    """Test alle 6 Kriterien"""
    llm = LMStudioClient()
    store = VectorStore()
    store.clear_all()
    
    # Comprehensive test document
    doc_text = """
    Unser Unternehmen TechInnovate GmbH hat seinen Sitz in Erfurt, Thüringen.
    Wir sind ein KMU mit 15 Mitarbeitern.
    Wir beantragen eine Förderung in Höhe von 150.000 Euro.
    Unser Projekt entwickelt eine innovative KI-Lösung (Innovationsgrad 8/10).
    Die Marktanalyse zeigt 500 potentielle Kunden und 3 Hauptwettbewerber.
    Der Finanzplan umfasst Umsatzprognose, Kostenplanung und Liquiditätsplanung.
    """
    
    chunks = chunk_text(doc_text, chunk_size=150, chunk_overlap=30)
    store.add_documents(
        chunks,
        [{"doc": "test", "chunk": i} for i in range(len(chunks))],
        [f"test_{i}" for i in range(len(chunks))]
    )
    
    # Check all criteria
    result = check_all_criteria(doc_text, llm, store)
    
    assert "overall" in result
    assert result["overall"] in ["PASSED", "FAILED"]
    assert "summary" in result
    assert "criteria" in result
    assert len(result["criteria"]) == 6
    
    # Verify summary
    summary = result["summary"]
    assert summary["passed"] + summary["failed"] + summary["unclear"] == 6
