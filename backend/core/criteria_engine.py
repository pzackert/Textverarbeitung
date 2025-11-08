"""
Kriterien-Engine für Document Verification System
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional

from backend.core.models import (
    CriteriaCatalog,
    Document,
    Criterion,
    CriterionTarget,
    CriterionPrompt,
    CriterionType
)


class CriteriaEngine:
    """Engine für Kriterienprüfung"""
    
    def __init__(self, catalog_path: Path):
        """
        Args:
            catalog_path: Pfad zur Kriterienkatalog JSON
        """
        self.catalog_path = catalog_path
        self.catalog: Optional[CriteriaCatalog] = None
        self.load_catalog()
    
    def load_catalog(self) -> None:
        """Lädt Kriterienkatalog aus JSON"""
        with open(self.catalog_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # JSON in Models umwandeln
        documents = []
        for doc in data['documents']:
            criteria = []
            for crit in doc['criteria']:
                target = CriterionTarget(
                    type=CriterionType(crit['target']['type']),
                    min=crit['target'].get('min'),
                    max=crit['target'].get('max'),
                    description=crit['target'].get('description'),
                    unit=crit['target'].get('unit')
                )
                
                prompt = CriterionPrompt(
                    role=crit['prompt']['role'],
                    instruction=crit['prompt']['instruction'],
                    expected_format=crit['prompt']['expected_format'],
                    validation_hints=crit['prompt'].get('validation_hints')
                )
                
                criterion = Criterion(
                    id=crit['id'],
                    name=crit['name'],
                    description=crit['description'],
                    target=target,
                    prompt=prompt
                )
                criteria.append(criterion)
            
            document = Document(
                type=doc['type'],
                name=doc['name'],
                description=doc['description'],
                supported_formats=doc['supported_formats'],
                required=doc['required'],
                criteria=criteria
            )
            documents.append(document)
        
        self.catalog = CriteriaCatalog(
            version=data['version'],
            last_updated=data['last_updated'],
            documents=documents
        )
    
    def get_document_criteria(self, doc_type: str) -> List[Criterion]:
        """
        Holt Kriterien für einen Dokumententyp.
        
        Args:
            doc_type: Typ des Dokuments
            
        Returns:
            Liste der Kriterien
        """
        if not self.catalog:
            raise ValueError("Katalog nicht geladen!")
            
        for doc in self.catalog.documents:
            if doc.type == doc_type:
                return doc.criteria
        
        raise ValueError(f"Dokumententyp {doc_type} nicht gefunden!")
    
    def evaluate_criterion(
        self,
        document_text: str,
        criterion: Criterion,
        llm_client: Any
    ) -> Dict[str, Any]:
        """
        Prüft ein Kriterium mittels LLM.
        
        Args:
            document_text: Text des Dokuments
            criterion: Zu prüfendes Kriterium
            llm_client: LLM Client
            
        Returns:
            Prüfergebnis als Dict
        """
        # Prompt zusammenbauen
        system_prompt = f"Du bist ein {criterion.prompt.role}. Deine Aufgabe ist es, ein Dokument nach spezifischen Kriterien zu prüfen."
        
        user_prompt = f"""
        Kriterium: {criterion.name}
        Beschreibung: {criterion.description}
        
        Dokument:
        {document_text}
        
        Anweisung:
        {criterion.prompt.instruction}
        
        Antworte nur mit dem erwarteten Wert ({criterion.prompt.expected_format}).
        """
        
        # LLM Antwort holen
        result = llm_client.generate(
            prompt=user_prompt,
            system_prompt=system_prompt
        )
        
        # Ergebnis parsen & validieren
        parsed_result = self._parse_result(result, criterion)
        
        return {
            "criterion_id": criterion.id,
            "criterion_name": criterion.name,
            "result": parsed_result,
            "passed": self._check_target(parsed_result, criterion.target)
        }
    
    def _parse_result(self, result: str, criterion: Criterion) -> Any:
        """Parst LLM Ergebnis in korrekten Typ"""
        result = result.strip().lower()
        
        if criterion.target.type == CriterionType.BOOLEAN:
            return result in ['true', 'yes', 'ja', '1']
        
        elif criterion.target.type in [CriterionType.NUMBER, CriterionType.SCORE]:
            try:
                return float(result.replace(',', '.'))
            except ValueError:
                raise ValueError(f"Konnte {result} nicht als Zahl parsen!")
                
        return result  # TEXT
    
    def _check_target(self, value: Any, target: CriterionTarget) -> bool:
        """Prüft ob Wert das Target erfüllt"""
        if target.type == CriterionType.BOOLEAN:
            return bool(value)
            
        elif target.type in [CriterionType.NUMBER, CriterionType.SCORE]:
            if target.min is not None and value < target.min:
                return False
            if target.max is not None and value > target.max:
                return False
            return True
            
        return True  # TEXT hat keine Zielwerte