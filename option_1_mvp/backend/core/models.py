"""
Core Models für Document Verification System
"""

from dataclasses import dataclass
from typing import List, Dict, Any, Optional
from enum import Enum


class CriterionType(Enum):
    """Typ eines Kriteriums"""
    BOOLEAN = "boolean"
    NUMBER = "number"
    SCORE = "score"
    TEXT = "text"


@dataclass
class CriterionTarget:
    """Zielwert eines Kriteriums"""
    type: CriterionType
    min: Optional[float] = None
    max: Optional[float] = None
    description: Optional[str] = None
    unit: Optional[str] = None


@dataclass
class CriterionPrompt:
    """Prompt-Definition für LLM"""
    role: str
    instruction: str
    expected_format: str
    validation_hints: Optional[List[str]] = None


@dataclass
class Criterion:
    """Ein einzelnes Prüfkriterium"""
    id: str
    name: str
    description: str
    target: CriterionTarget
    prompt: CriterionPrompt


@dataclass
class Document:
    """Dokumentendefinition"""
    type: str
    name: str
    description: str
    supported_formats: List[str]
    required: bool
    criteria: List[Criterion]


@dataclass
class CriteriaCatalog:
    """Gesamter Kriterienkatalog"""
    version: str
    last_updated: str
    documents: List[Document]