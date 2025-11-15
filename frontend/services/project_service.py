"""Project service helpers for the Streamlit frontend."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from backend.projekt_manager import (
    create_projekt,
    load_projekt_metadata,
    update_projekt_metadata,
)

PROJECTS_DIR = Path("data/projects")
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)
CATALOG_PATH = Path("config/criteria_catalog.json")

STATUS_STEP_MAP = {
    "created": 1,
    "metadata": 1,
    "uploading": 2,
    "documents": 2,
    "uploaded": 3,
    "checking": 3,
    "checked": 4,
    "completed": 4,
}


@dataclass
class ProjectRecord:
    """Normalized view on project metadata for UI consumption."""

    id: str
    name: str
    status: str
    current_step: int
    created_at: str
    updated_at: str
    description: Optional[str] = None
    applicant: Optional[str] = None
    modul: Optional[str] = None
    project_type: Optional[str] = None
    result: Optional[str] = None
    documents: List[Dict[str, Any]] = field(default_factory=list)
    is_demo: bool = False
    last_check_at: Optional[str] = None
    last_upload_at: Optional[str] = None

    @property
    def status_label(self) -> str:
        mapping = {
            "created": "Neu",
            "uploading": "Upload offen",
            "uploaded": "Upload abgeschlossen",
            "checking": "Pruefung laeuft",
            "checked": "Geprueft",
            "completed": "Abgeschlossen",
        }
        return mapping.get(self.status, self.status.capitalize())

    @property
    def table_row(self) -> Dict[str, Any]:
        return {
            "Projekt": self.name,
            "Status": self.status_label,
            "Schritt": f"{self.current_step}/4",
            "Ergebnis": self.result or "-",
            "Zuletzt aktualisiert": self.updated_at[:19].replace("T", " "),
        }


def _ensure_metadata_schema(project_dir: Path) -> Optional[Dict[str, Any]]:
    metadata_file = project_dir / "metadata.json"
    if metadata_file.exists():
        with open(metadata_file, "r", encoding="utf-8") as handle:
            return json.load(handle)

    legacy_file = project_dir / "meta.json"
    if not legacy_file.exists():
        return None

    with open(legacy_file, "r", encoding="utf-8") as handle:
        legacy = json.load(handle)

    projekt_id = (
        legacy.get("projekt_id")
        or legacy.get("id")
        or project_dir.name
    )
    timestamp = legacy.get("created") or datetime.now().isoformat()
    metadata = {
        "projekt_id": projekt_id,
        "projekt_name": legacy.get("projekt_name")
        or legacy.get("name")
        or projekt_id.replace("_", " ").title(),
        "antragsteller": legacy.get("antragsteller") or "Demo GmbH",
        "modul": legacy.get("modul") or "PROFI Standard",
        "projektart": legacy.get("projektart") or "Forschung",
        "beschreibung": legacy.get("beschreibung"),
        "status": legacy.get("status", "created"),
        "current_step": legacy.get(
            "current_step",
            STATUS_STEP_MAP.get(legacy.get("status", "created"), 1),
        ),
        "created_at": timestamp,
        "updated_at": timestamp,
        "documents": legacy.get("documents", []),
    }
    metadata_file.write_text(
        json.dumps(metadata, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return metadata


def _load_metadata(project_id: str) -> Optional[Dict[str, Any]]:
    project_dir = PROJECTS_DIR / project_id
    if not project_dir.exists():
        return None

    data = _ensure_metadata_schema(project_dir)
    if data:
        return data

    metadata_file = project_dir / "metadata.json"
    if not metadata_file.exists():
        return None

    with open(metadata_file, "r", encoding="utf-8") as handle:
        return json.load(handle)


def _to_record(metadata: Dict[str, Any]) -> ProjectRecord:
    status = metadata.get("status", "created")
    current_step = int(
        metadata.get("current_step")
        or STATUS_STEP_MAP.get(status, 1)
    )
    return ProjectRecord(
        id=(
            metadata.get("projekt_id")
            or metadata.get("id")
            or ""
        ).strip()
        or "unbekannt",
        name=(
            metadata.get("projekt_name")
            or metadata.get("name")
            or metadata.get("projekt_id")
            or "Unbenanntes Projekt"
        ),
        status=status,
        current_step=current_step,
        created_at=metadata.get("created_at")
        or metadata.get("created")
        or datetime.now().isoformat(),
        updated_at=metadata.get("updated_at")
        or metadata.get("created_at")
        or datetime.now().isoformat(),
        description=metadata.get("beschreibung"),
        applicant=metadata.get("antragsteller"),
        modul=metadata.get("modul"),
        project_type=metadata.get("projektart"),
        result=metadata.get("result"),
        documents=metadata.get("documents", []),
        is_demo=metadata.get("is_demo", False),
        last_check_at=metadata.get("last_check_at"),
        last_upload_at=metadata.get("last_upload_at"),
    )


def list_projects(limit: int = 50) -> List[ProjectRecord]:
    records: List[ProjectRecord] = []
    for project_dir in PROJECTS_DIR.iterdir():
        if not project_dir.is_dir():
            continue
        metadata = _load_metadata(project_dir.name)
        if not metadata:
            continue
        records.append(_to_record(metadata))

    records.sort(key=lambda rec: rec.updated_at, reverse=True)
    return records[:limit]


def create_project(form_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[str]]:
    projekt_name = form_data.get("projekt_name")
    antragsteller = form_data.get("antragsteller") or "Unbekannt"
    modul = form_data.get("modul") or "PROFI Standard"
    projektart = form_data.get("projektart") or "Forschung"
    beschreibung = form_data.get("beschreibung")

    if not projekt_name:
        return None, "Projektname ist erforderlich"

    projekt_id = create_projekt(
        projekt_name,
        antragsteller,
        modul,
        projektart,
        beschreibung,
    )
    update_fields = {
        "beschreibung": beschreibung,
        "status": "created",
        "current_step": 1,
    }
    update_projekt_metadata(projekt_id, update_fields)
    return projekt_id, None


def get_project(project_id: Optional[str]) -> Optional[ProjectRecord]:
    if not project_id:
        return None
    try:
        metadata = load_projekt_metadata(project_id)
    except FileNotFoundError:
        metadata = _load_metadata(project_id)
    if not metadata:
        return None
    return _to_record(metadata)


def mark_step(project_id: str, status: str, current_step: int) -> None:
    update_projekt_metadata(
        project_id,
        {"status": status, "current_step": current_step},
    )


def load_catalog() -> Dict[str, Any]:
    if not CATALOG_PATH.exists():
        return {"documents": [], "criteria": []}
    with open(CATALOG_PATH, "r", encoding="utf-8") as handle:
        try:
            return json.load(handle)
        except json.JSONDecodeError:
            return {"documents": [], "criteria": []}


def get_required_documents() -> List[Dict[str, Any]]:
    catalog = load_catalog()
    return catalog.get("documents", [])


def required_documents_status(record: Optional[ProjectRecord]) -> Dict[str, bool]:
    if not record:
        return {}
    catalog = load_catalog()
    required_docs = [
        doc
        for doc in catalog.get("documents", [])
        if doc.get("required")
    ]
    uploaded_types = {
        doc.get("doc_type") or doc.get("type")
        for doc in record.documents
    }
    status: Dict[str, bool] = {}
    for doc in required_docs:
        doc_type = doc.get("type")
        if not doc_type:
            continue
        status[doc_type] = doc_type in uploaded_types
    return status


def ensure_demo_project() -> Optional[str]:
    records = list_projects()
    for record in records:
        if record.is_demo:
            return record.id

    projekt_id = create_projekt(
        "Demo Wasserstoffspeicher",
        "FutureEnergy GmbH",
        "PROFI Standard",
        "Entwicklung",
        "Referenzprojekt fuer Live-Demo",
    )
    now = datetime.now().isoformat()
    demo_updates = {
        "status": "checked",
        "current_step": 4,
        "beschreibung": "Vollstaendig durchlaufener Musterantrag",
        "result": "PASSED",
        "is_demo": True,
        "documents": [
            {
                "doc_id": "demo-business-plan",
                "doc_type": "business_plan",
                "filename": "demo_geschaeftsplan.pdf",
                "original_filename": "Demo_Geschaeftsplan.pdf",
                "uploaded_at": now,
            },
            {
                "doc_id": "demo-finance",
                "doc_type": "financial_documents",
                "filename": "demo_finanzplan.xlsx",
                "original_filename": "Demo_Finanzplan.xlsx",
                "uploaded_at": now,
            },
        ],
        "last_upload_at": now,
        "last_check_at": now,
    }
    update_projekt_metadata(projekt_id, demo_updates)

    project_dir = PROJECTS_DIR / projekt_id
    project_dir.mkdir(parents=True, exist_ok=True)
    sample_result = {
        "overall": "PASSED",
        "summary": {"passed": 5, "failed": 1, "unclear": 0},
        "criteria": [
            {
                "id": "company_location",
                "name": "Unternehmenssitz in Thueringen",
                "result": "PASSED",
                "answer": "Der Hauptsitz befindet sich in Erfurt.",
                "context_used": 2,
            },
            {
                "id": "kmu_status",
                "name": "KMU-Status",
                "result": "PASSED",
                "answer": "FutureEnergy erfuellt alle KMU-Kriterien.",
                "context_used": 3,
            },
            {
                "id": "funding_amount",
                "name": "Foerdersumme unter Limit",
                "result": "PASSED",
                "answer": "Beantragte Summe: 180.000 EUR.",
                "context_used": 1,
            },
            {
                "id": "innovation_degree",
                "name": "Innovationsgrad",
                "result": "PASSED",
                "answer": "Innovation Score: 8/10",
                "context_used": 2,
            },
            {
                "id": "market_analysis",
                "name": "Marktanalyse vorhanden",
                "result": "FAILED",
                "answer": "Es fehlen Daten zur Konkurrenzanalyse.",
                "context_used": 1,
            },
            {
                "id": "financial_plan",
                "name": "Finanzplan plausibel",
                "result": "PASSED",
                "answer": "Finanzplan inklusive Liquiditaetsplanung vorhanden.",
                "context_used": 2,
            },
        ],
    }
    (project_dir / "results.json").write_text(
        json.dumps(sample_result, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    return projekt_id


def refresh_records() -> List[ProjectRecord]:
    return list_projects()


def load_results(project_id: Optional[str]) -> Optional[Dict[str, Any]]:
    if not project_id:
        return None
    results_path = PROJECTS_DIR / project_id / "results.json"
    if not results_path.exists():
        return None
    try:
        with open(results_path, "r", encoding="utf-8") as handle:
            return json.load(handle)
    except json.JSONDecodeError:
        return None