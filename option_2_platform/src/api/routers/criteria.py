from typing import List
from fastapi import APIRouter, HTTPException, status
from src.api.schemas_criteria import Criterion, CreateCriterionRequest, UpdateCriterionRequest
from src.services.criteria_service import criteria_service

router = APIRouter(prefix="/criteria", tags=["criteria"])

@router.get("", response_model=List[Criterion])
async def list_criteria():
    return criteria_service.get_all()

@router.get("/{criterion_id}", response_model=Criterion)
async def get_criterion(criterion_id: str):
    criterion = criteria_service.get_by_id(criterion_id)
    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    return criterion

@router.post("", response_model=Criterion, status_code=status.HTTP_201_CREATED)
async def create_criterion(request: CreateCriterionRequest):
    try:
        return criteria_service.create(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{criterion_id}", response_model=Criterion)
async def update_criterion(criterion_id: str, request: UpdateCriterionRequest):
    criterion = criteria_service.update(criterion_id, request)
    if not criterion:
        raise HTTPException(status_code=404, detail="Criterion not found")
    return criterion

@router.delete("/{criterion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_criterion(criterion_id: str):
    success = criteria_service.delete(criterion_id)
    if not success:
        raise HTTPException(status_code=404, detail="Criterion not found")
    return None
