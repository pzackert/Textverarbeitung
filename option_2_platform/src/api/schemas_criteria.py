from typing import List, Optional
from pydantic import BaseModel

class Criterion(BaseModel):
    id: str
    name: str
    kategorie: str
    kurz: str
    lang: str
    prompt: Optional[str] = None
    recommended: bool = False

class CriteriaCatalog(BaseModel):
    criteria: List[Criterion]

class CreateCriterionRequest(BaseModel):
    id: str
    name: str
    kategorie: str
    kurz: str
    lang: str
    prompt: Optional[str] = None
    recommended: bool = False

class UpdateCriterionRequest(BaseModel):
    name: Optional[str] = None
    kategorie: Optional[str] = None
    kurz: Optional[str] = None
    lang: Optional[str] = None
    prompt: Optional[str] = None
    recommended: Optional[bool] = None
