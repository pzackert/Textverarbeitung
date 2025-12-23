import json
import logging
import os
from typing import List, Optional
from pathlib import Path
from src.api.schemas_criteria import Criterion, CreateCriterionRequest, UpdateCriterionRequest

logger = logging.getLogger(__name__)

class CriteriaService:
    def __init__(self, config_path: str = "config/criteria_catalog.json"):
        self.config_path = Path(config_path)
        self._ensure_config_exists()

    def _ensure_config_exists(self):
        if not self.config_path.exists():
            logger.warning(f"Criteria catalog not found at {self.config_path}, creating default.")
            self.config_path.parent.mkdir(parents=True, exist_ok=True)
            self._save_criteria([])

    def _load_criteria(self) -> List[dict]:
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                # Support both keys, prefer 'kriterien' from the provided file
                return data.get("kriterien", data.get("criteria", []))
        except Exception as e:
            logger.error(f"Failed to load criteria: {e}")
            return []

    def _save_criteria(self, criteria_list: List[dict]):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                # Use 'kriterien' to stay consistent with the provided file
                json.dump({"version": "1.0", "kriterien": criteria_list}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save criteria: {e}")
            raise e

    def get_all(self) -> List[Criterion]:
        raw_list = self._load_criteria()
        return [Criterion(**item) for item in raw_list]

    def get_by_id(self, criterion_id: str) -> Optional[Criterion]:
        criteria = self.get_all()
        for c in criteria:
            if c.id == criterion_id:
                return c
        return None

    def get_criterion(self, criterion_id: str) -> Optional[Criterion]:
        """Backward-compatible alias for get_by_id."""
        return self.get_by_id(criterion_id)

    def create(self, request: CreateCriterionRequest) -> Criterion:
        criteria = self.get_all()
        if any(c.id == request.id for c in criteria):
            raise ValueError(f"Criterion with ID {request.id} already exists.")
        
        new_criterion = Criterion(**request.dict())
        # Convert to dict for storage
        raw_list = [c.dict() for c in criteria]
        raw_list.append(new_criterion.dict())
        self._save_criteria(raw_list)
        return new_criterion

    def update(self, criterion_id: str, request: UpdateCriterionRequest) -> Optional[Criterion]:
        criteria = self.get_all()
        target_index = next((i for i, c in enumerate(criteria) if c.id == criterion_id), None)
        
        if target_index is None:
            return None
        
        current_data = criteria[target_index].dict()
        update_data = request.dict(exclude_unset=True)
        
        updated_data = {**current_data, **update_data}
        updated_criterion = Criterion(**updated_data)
        
        # Save back
        raw_list = [c.dict() for c in criteria]
        raw_list[target_index] = updated_criterion.dict()
        self._save_criteria(raw_list)
        
        return updated_criterion

    def delete(self, criterion_id: str) -> bool:
        criteria = self.get_all()
        initial_len = len(criteria)
        criteria = [c for c in criteria if c.id != criterion_id]
        
        if len(criteria) < initial_len:
            raw_list = [c.dict() for c in criteria]
            self._save_criteria(raw_list)
            return True
        return False

criteria_service = CriteriaService()
