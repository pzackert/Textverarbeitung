import json
import uuid
import os
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from src.core.models import Project, Document

# Resolve data folder independently of current working directory
BASE_DIR = Path(__file__).resolve().parents[2]
INPUT_ROOT = BASE_DIR / "data" / "input"
DEFAULT_METADATA = {
    "name": None,
    "description": None,
    "applicant": None,
    "funding_amount": None,
    "status": "Entwurf",
}


def _write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def _ensure_minimal_project_structure(project_dir: Path, project_id: str) -> None:
    """Create or heal minimal project files and folders."""
    uploads = project_dir / "uploads"
    annotated = project_dir / "annotated"
    uploads.mkdir(parents=True, exist_ok=True)
    annotated.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    # metadata.json (heal if missing or invalid)
    meta_path = project_dir / "metadata.json"
    meta: Dict[str, Any]
    try:
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            if not isinstance(meta, dict):
                raise ValueError("metadata not a dict")
        else:
            meta = {}
    except Exception:
        meta = {}

    meta.setdefault("id", project_id)
    meta.setdefault("name", project_id)
    meta.setdefault("description", None)
    meta.setdefault("applicant", None)
    meta.setdefault("funding_amount", None)
    meta.setdefault("status", "Entwurf")
    meta.setdefault("created_at", now)
    meta.setdefault("updated_at", meta.get("created_at") or now)
    _write_json(meta_path, meta)

    # chat_history.json (heal invalid shapes)
    chat_path = project_dir / "chat_history.json"
    try:
        chat_data = json.loads(chat_path.read_text(encoding="utf-8")) if chat_path.exists() else {"messages": []}
        if not isinstance(chat_data, dict) or "messages" not in chat_data or not isinstance(chat_data.get("messages"), list):
            raise ValueError("invalid chat format")
    except Exception:
        chat_data = {"messages": []}
    _write_json(chat_path, chat_data)

    # criteria_responses.json handled by criteria_results_store with self-healing
    from src.services.criteria_results_store import load_criteria_results
    load_criteria_results(project_id)


def _read_metadata(project_dir: Path, project_id: str) -> Dict:
    meta_path = project_dir / "metadata.json"
    try:
        with meta_path.open("r", encoding="utf-8") as f:
            data = json.load(f)
            data.setdefault("id", project_id)
            return data
    except Exception:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return {
            "id": project_id,
            "name": project_id,
            "description": None,
            "applicant": None,
            "funding_amount": None,
            "status": "Entwurf",
            "created_at": now,
            "updated_at": now,
        }

class ProjectService:
    def __init__(self):
        INPUT_ROOT.mkdir(parents=True, exist_ok=True)
        self.INPUT_ROOT = INPUT_ROOT

    def heal_all_projects(self) -> List[Dict[str, Any]]:
        """Scan input root, heal minimal structure, and report results."""
        reports: List[Dict[str, Any]] = []
        if not INPUT_ROOT.exists():
            return reports
        for pdir in INPUT_ROOT.iterdir():
            if not pdir.is_dir() or pdir.name.startswith('.'):
                continue
            project_id = pdir.name
            _ensure_minimal_project_structure(pdir, project_id)
            reports.append({"project_id": project_id, "status": "healed"})
        return reports
    
    def _scan_projects(self) -> Dict[str, Project]:
        projects: Dict[str, Project] = {}
        if not INPUT_ROOT.exists():
            return projects
        for pdir in INPUT_ROOT.iterdir():
            if not pdir.is_dir() or pdir.name.startswith('.'):  # ignore hidden
                continue
            project_id = pdir.name
            _ensure_minimal_project_structure(pdir, project_id)
            meta = _read_metadata(pdir, project_id)

            # Build documents from uploads
            uploads_dir = pdir / "uploads"
            docs: List[Document] = []
            if uploads_dir.exists():
                for f in uploads_dir.iterdir():
                    if f.is_file() and not f.name.startswith('.'):
                        docs.append(
                            Document(
                                filename=f.name,
                                path=str(f),
                                size=f.stat().st_size,
                                uploaded_at=datetime.fromtimestamp(f.stat().st_mtime)
                            )
                        )

            created_at = meta.get("created_at") or datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
            updated_at = meta.get("updated_at") or created_at

            try:
                proj = Project(
                    id=project_id,
                    name=meta.get("name") or project_id,
                    description=meta.get("description"),
                    applicant=meta.get("applicant"),
                    funding_amount=meta.get("funding_amount"),
                    status=meta.get("status", "Entwurf"),
                    created_at=datetime.fromisoformat(created_at.replace("Z","")),
                    updated_at=datetime.fromisoformat(updated_at.replace("Z","")),
                    documents=docs,
                )
            except Exception:
                proj = Project(
                    id=project_id,
                    name=project_id,
                    status="Entwurf",
                    documents=docs,
                )
            proj.doc_count = len(docs)
            projects[project_id] = proj
        return projects
    
    def create_project(self, name: str, description: Optional[str] = None, applicant: Optional[str] = None, funding_amount: Optional[float] = None) -> Project:
        """Create new project folder with minimal structure."""
        project = Project(
            name=name,
            description=description,
            applicant=applicant,
            funding_amount=funding_amount,
            status="Entwurf",
        )
        project_dir = INPUT_ROOT / project.id
        project_dir.mkdir(parents=True, exist_ok=True)
        _ensure_minimal_project_structure(project_dir, project.id)

        # Write metadata.json
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        meta = {
            "id": project.id,
            "name": name,
            "description": description,
            "applicant": applicant,
            "funding_amount": funding_amount,
            "status": "Entwurf",
            "created_at": now,
            "updated_at": now,
        }
        (project_dir / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

        return project
    
    def update_project_status(self, project_id: str, status: str) -> Optional[Project]:
        """Update project status in metadata.json."""
        project_dir = INPUT_ROOT / project_id
        if not project_dir.exists():
            return None
        meta = _read_metadata(project_dir, project_id)
        meta["status"] = status
        meta["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        (project_dir / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        return self.get_project(project_id)

    def delete_project(self, project_id: str) -> bool:
        """Delete project folder."""
        project_dir = INPUT_ROOT / project_id
        if project_dir.exists():
            import shutil
            shutil.rmtree(project_dir)
            return True
        return False

    def list_projects(self) -> List[Project]:
        """List all projects from folder scan."""
        projects = self._scan_projects()
        return sorted(projects.values(), key=lambda p: p.created_at, reverse=True)

    def _validate_documents(self, project: Project) -> Project:
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        projects = self._scan_projects()
        return projects.get(project_id)

    def save_document(self, project_id: str, filename: str, content: bytes) -> Optional[Document]:
        project_dir = INPUT_ROOT / project_id
        if not project_dir.exists():
            return None

        uploads_dir = project_dir / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        file_path = uploads_dir / filename

        with open(file_path, "wb") as f:
            f.write(content)
            
        doc = Document(
            filename=filename, 
            path=str(file_path),
            size=len(content)
        )
        return doc

    def update_project(self, project: Project) -> None:
        project_dir = INPUT_ROOT / project.id
        if not project_dir.exists():
            return
        meta = _read_metadata(project_dir, project.id)
        meta.update({
            "name": project.name,
            "description": project.description,
            "applicant": project.applicant,
            "funding_amount": project.funding_amount,
            "status": project.status,
            "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        })
        (project_dir / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

# Singleton instance
project_service = ProjectService()
