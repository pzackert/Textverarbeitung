"""Criteria Engine - 6 Basis-Kriterien für MVP"""
from typing import Dict, Any, List
from backend.llm.lm_studio_client import LMStudioClient
from backend.rag.vector_store import VectorStore
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)

# 6 Basis-Kriterien für MVP
CRITERIA = [
    {
        "id": "company_location",
        "name": "Unternehmenssitz in Thüringen",
        "prompt": "Ist das Unternehmen in Thüringen ansässig? Antworte nur mit JA oder NEIN."
    },
    {
        "id": "kmu_status",
        "name": "KMU-Status",
        "prompt": "Ist das Unternehmen ein KMU (Kleine und Mittlere Unternehmen)? Antworte nur mit JA oder NEIN."
    },
    {
        "id": "funding_amount",
        "name": "Fördersumme unter Limit",
        "prompt": "Liegt die beantragte Fördersumme unter 200.000 Euro? Antworte nur mit JA oder NEIN."
    },
    {
        "id": "innovation_degree",
        "name": "Innovationsgrad",
        "prompt": "Hat das Projekt einen ausreichenden Innovationsgrad? Bewerte auf einer Skala von 1-10 und gib nur die Zahl zurück."
    },
    {
        "id": "market_analysis",
        "name": "Marktanalyse vorhanden",
        "prompt": "Enthält der Geschäftsplan eine vollständige Marktanalyse (Wettbewerber, Zielgruppe, Marktpotential)? Antworte nur mit JA oder NEIN."
    },
    {
        "id": "financial_plan",
        "name": "Finanzplan plausibel",
        "prompt": "Ist der Finanzplan vollständig und plausibel (Umsatzprognose, Kostenplanung, Liquiditätsplanung)? Antworte nur mit JA oder NEIN."
    }
]


def check_criterion(criterion_id: str, document_text: str, llm: LMStudioClient, vector_store: VectorStore) -> Dict[str, Any]:
    """Prüfe einzelnes Kriterium"""
    criterion = next((c for c in CRITERIA if c["id"] == criterion_id), None)
    if not criterion:
        return {"id": criterion_id, "result": "ERROR", "reason": "Unbekanntes Kriterium"}
    
    # Hole relevante Chunks aus RAG
    results = vector_store.search(criterion["prompt"], top_k=3)
    context = [r["text"] for r in results]
    
    # LLM mit RAG-Kontext
    answer = llm.generate_with_context(criterion["prompt"], context)
    
    # Extrahiere Ergebnis (vereinfacht)
    answer_upper = answer.upper()
    if "JA" in answer_upper and "NEIN" not in answer_upper:
        result = "PASSED"
    elif "NEIN" in answer_upper:
        result = "FAILED"
    elif any(char.isdigit() for char in answer):
        # Score-based (Innovation)
        score = int(''.join(filter(str.isdigit, answer)))
        result = "PASSED" if score >= 7 else "FAILED"
    else:
        result = "UNCLEAR"
    
    logger.info(f"✓ Kriterium '{criterion['name']}': {result}")
    return {
        "id": criterion_id,
        "name": criterion["name"],
        "result": result,
        "answer": answer,
        "context_used": len(context)
    }


def check_all_criteria(document_text: str, llm: LMStudioClient, vector_store: VectorStore) -> Dict[str, Any]:
    """Prüfe alle 6 Kriterien"""
    logger.info("Starte Kriterienprüfung für alle 6 Kriterien...")
    
    results = []
    for criterion in CRITERIA:
        result = check_criterion(criterion["id"], document_text, llm, vector_store)
        results.append(result)
    
    passed = sum(1 for r in results if r["result"] == "PASSED")
    failed = sum(1 for r in results if r["result"] == "FAILED")
    unclear = sum(1 for r in results if r["result"] == "UNCLEAR")
    
    overall = "PASSED" if failed == 0 and unclear == 0 else "FAILED"
    
    logger.info(f"✓ Kriterienprüfung abgeschlossen: {passed} PASSED, {failed} FAILED, {unclear} UNCLEAR")
    
    return {
        "overall": overall,
        "summary": {"passed": passed, "failed": failed, "unclear": unclear},
        "criteria": results
    }
