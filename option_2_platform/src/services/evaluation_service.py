import logging
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel

from src.api.schemas_application import Application
from src.api.schemas_criteria import Criterion
from src.services.criteria_service import criteria_service
from src.services.application_service import application_service
from src.rag.llm_chain import LLMChain

logger = logging.getLogger(__name__)

class EvaluationResult(BaseModel):
    criterion_id: str
    criterion_name: str
    score: int # 0-10 or 1-3? Let's say 0=Fail, 1=Pass, 2=Unknown? Or 0-100?
    # Simple traffic light: "green", "yellow", "red"
    status: str 
    reasoning: str
    citations: List[Any] = []
    timestamp: datetime = datetime.utcnow()

class EvaluationReport(BaseModel):
    app_id: str
    results: List[EvaluationResult]
    summary: str
    created_at: datetime = datetime.utcnow()

class EvaluationService:
    def __init__(self):
        pass

    def evaluate_application(self, app_id: str, llm_chain: LLMChain) -> EvaluationReport:
        app = application_service.get_application(app_id)
        if not app:
            raise ValueError("Application not found")
        
        criteria_list = criteria_service.get_all()
        results = []
        
        logger.info(f"Starting evaluation for {app_id} with {len(criteria_list)} criteria")
        
        for criterion in criteria_list:
            if not criterion.active:
                continue
                
            try:
                # Formulate Query
                query = f"Prüfe das folgende Kriterium: {criterion.name}. {criterion.description}. {criterion.prompt or ''}"
                
                # Execute RAG Query
                response = llm_chain.query(
                    question=query,
                    metadata_filter={"project_id": app_id}
                )
                
                answer = response.get("answer", "")
                citations = response.get("citations", [])
                
                # Heuristic status determination (Real impl would use structured output)
                status = "yellow"
                if "ja" in answer.lower() or "erfüllt" in answer.lower():
                    status = "green"
                elif "nein" in answer.lower() or "nicht erfüllt" in answer.lower():
                    status = "red"
                    
                results.append(EvaluationResult(
                    criterion_id=criterion.id,
                    criterion_name=criterion.name,
                    score=0, # Placeholder
                    status=status,
                    reasoning=answer,
                    citations=citations
                ))
                
            except Exception as e:
                logger.error(f"Failed to evaluate criterion {criterion.id}: {e}")
                results.append(EvaluationResult(
                    criterion_id=criterion.id,
                    criterion_name=criterion.name,
                    score=0,
                    status="error",
                    reasoning=f"Fehler bei der Prüfung: {str(e)}"
                ))
        
        # Generate Summary
        summary = f"Prüfung abgeschlossen. {len(results)} Kriterien geprüft."
        
        # Store results in Application (we need to update the Schema first, but for now we can store in a JSON file or generic dict)
        # Application schema doesn't have `validation_results` detailed field yet.
        # But `Application` inherits from `ApplicationBase`.
        # I should probably save this report to `data/applications/{id}/evaluation.json`
        
        report = EvaluationReport(
            app_id=app_id,
            results=results,
            summary=summary
        )
        
        self._save_report(app_id, report)
        
        return report

    def _save_report(self, app_id: str, report: EvaluationReport):
        path = application_service.base_path / app_id / "evaluation.json"
        with open(path, "w", encoding="utf-8") as f:
            f.write(report.json())

    def get_latest_report(self, app_id: str) -> Optional[EvaluationReport]:
        path = application_service.base_path / app_id / "evaluation.json"
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = f.read()
                return EvaluationReport.parse_raw(data)
        except Exception:
            return None

evaluation_service = EvaluationService()
