import json
import uuid
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime, timezone
from src.api.schemas_application import Application, ApplicationCreate, ApplicationUpdate, ApplicationDocument, ApplicationSummary

logger = logging.getLogger(__name__)


def _parse_dt(value: Optional[str]) -> datetime:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except Exception:
            return datetime.now(timezone.utc)
    return datetime.now(timezone.utc)


class ApplicationService:
    """Folder-first application store without registry.json."""

    def __init__(self, base_path: str = "data/input"):
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)

    def _metadata_path(self, app_id: str) -> Path:
        return self.base_path / app_id / "metadata.json"

    def _uploads_dir(self, app_id: str) -> Path:
        # Prefer uploads; fall back to legacy input only when it already exists
        uploads = self.base_path / app_id / "uploads"
        legacy_input = self.base_path / app_id / "input"
        if uploads.exists() or not legacy_input.exists():
            return uploads
        return legacy_input

    def _annotated_dir(self, app_id: str) -> Path:
        return self.base_path / app_id / "annotated"

    def _ensure_structure(self, app_id: str) -> None:
        (self.base_path / app_id).mkdir(parents=True, exist_ok=True)
        self._uploads_dir(app_id).mkdir(parents=True, exist_ok=True)
        self._annotated_dir(app_id).mkdir(parents=True, exist_ok=True)

    def _default_metadata(self, app_id: str) -> Dict:
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        return {
            "id": app_id,
            "title": f"Imported Application {app_id[:8]}",
            "applicant": "Unknown Applicant",
            "description": None,
            "funding_request": None,
            "status": "analyzed",
            "created_at": now,
            "updated_at": now,
            "documents": [],
        }

    def _read_metadata(self, app_id: str) -> Dict:
        path = self._metadata_path(app_id)
        meta = self._default_metadata(app_id)
        try:
            if path.exists():
                loaded = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(loaded, dict):
                    meta.update(loaded)
        except Exception as exc:
            logger.warning(f"metadata.json invalid for {app_id}: {exc}")

        # Normalize keys from project metadata if present
        if meta.get("name") and not meta.get("title"):
            meta["title"] = meta.get("name")
        if not meta.get("title"):
            meta["title"] = meta.get("id")

        # Ensure timestamps exist
        meta.setdefault("created_at", datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"))
        meta.setdefault("updated_at", meta["created_at"])
        meta.setdefault("documents", meta.get("documents", []))
        return meta

    def _write_metadata(self, app_id: str, meta: Dict) -> None:
        path = self._metadata_path(app_id)
        path.parent.mkdir(parents=True, exist_ok=True)

        def _ser(val):
            if isinstance(val, datetime):
                return val.isoformat().replace("+00:00", "Z")
            if isinstance(val, list):
                return [_ser(v) for v in val]
            if isinstance(val, dict):
                return {k: _ser(v) for k, v in val.items()}
            return val

        safe_meta = {k: _ser(v) for k, v in meta.items()}
        path.write_text(json.dumps(safe_meta, ensure_ascii=False, indent=2), encoding="utf-8")

    def _list_documents(self, app_id: str, meta_docs: Dict[str, Dict]) -> List[ApplicationDocument]:
        uploads_dir = self._uploads_dir(app_id)
        annotated_dir = self._annotated_dir(app_id)
        docs: List[ApplicationDocument] = []
        if not uploads_dir.exists():
            return docs

        for f in uploads_dir.iterdir():
            if not f.is_file() or f.name.startswith('.'):
                continue
            annotated = annotated_dir / f"{f.stem}_annotated{f.suffix}"
            meta_doc = meta_docs.get(f.name, {})
            docs.append(
                ApplicationDocument(
                    filename=f.name,
                    size_bytes=f.stat().st_size,
                    content_type="application/pdf" if f.suffix.lower() == ".pdf" else "application/octet-stream",
                    uploaded_at=_parse_dt(meta_doc.get("uploaded_at")) if meta_doc else datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc),
                    is_indexed=bool(meta_doc.get("is_indexed", False)),
                    has_annotated_version=annotated.exists(),
                )
            )
        return docs

    def list_applications(self) -> List[ApplicationSummary]:
        apps: List[ApplicationSummary] = []
        if not self.base_path.exists():
            return apps

        for item in self.base_path.iterdir():
            if not item.is_dir() or item.name.startswith('.'):
                continue
            if item.name in {"output", "annotated", "uploads"}:
                continue

            meta = self._read_metadata(item.name)
            meta_docs = {d.get("filename"): d for d in meta.get("documents", []) if isinstance(d, dict) and d.get("filename")}
            documents = self._list_documents(item.name, meta_docs)
            apps.append(
                ApplicationSummary(
                    id=meta.get("id", item.name),
                    title=meta.get("title", item.name),
                    applicant=meta.get("applicant") or "Unknown Applicant",
                    status=meta.get("status", "analyzed"),
                    created_at=_parse_dt(meta.get("created_at")),
                    updated_at=_parse_dt(meta.get("updated_at")),
                    document_count=len(documents),
                )
            )

        return sorted(apps, key=lambda a: a.updated_at, reverse=True)

    def get_application(self, app_id: str) -> Optional[Application]:
        app_dir = self.base_path / app_id
        if not app_dir.exists():
            return None

        meta = self._read_metadata(app_id)
        meta_docs = {d.get("filename"): d for d in meta.get("documents", []) if isinstance(d, dict) and d.get("filename")}
        documents = self._list_documents(app_id, meta_docs)

        return Application(
            id=meta.get("id", app_id),
            title=meta.get("title", app_id),
            applicant=meta.get("applicant") or "Unknown Applicant",
            description=meta.get("description"),
            funding_request=meta.get("funding_request"),
            status=meta.get("status", "draft"),
            created_at=_parse_dt(meta.get("created_at")),
            updated_at=_parse_dt(meta.get("updated_at")),
            documents=documents,
            rag_status=meta.get("rag_status", "pending"),
        )

    def create_application(self, req: ApplicationCreate) -> Application:
        app_id = str(uuid.uuid4())
        self._ensure_structure(app_id)
        now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

        meta = {
            "id": app_id,
            "title": req.title,
            "applicant": req.applicant,
            "description": req.description,
            "funding_request": req.funding_request,
            "status": "draft",
            "created_at": now,
            "updated_at": now,
            "documents": [],
            "rag_status": "pending",
        }
        self._write_metadata(app_id, meta)

        return Application(
            id=app_id,
            title=req.title,
            applicant=req.applicant,
            description=req.description,
            funding_request=req.funding_request,
            status="draft",
            created_at=_parse_dt(now),
            updated_at=_parse_dt(now),
            documents=[],
        )

    def update_application(self, app_id: str, updates: ApplicationUpdate) -> Optional[Application]:
        if not (self.base_path / app_id).exists():
            return None

        meta = self._read_metadata(app_id)
        update_dict = updates.dict(exclude_unset=True)
        meta.update(update_dict)
        meta["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._write_metadata(app_id, meta)
        return self.get_application(app_id)

    def delete_application(self, app_id: str) -> bool:
        app_dir = self.base_path / app_id
        if not app_dir.exists():
            return False
        shutil.rmtree(app_dir, ignore_errors=True)
        return True

    def add_document(self, app_id: str, filename: str, content: bytes) -> Optional[ApplicationDocument]:
        app_dir = self.base_path / app_id
        if not app_dir.exists():
            return None

        self._ensure_structure(app_id)
        uploads_dir = self._uploads_dir(app_id)
        file_path = uploads_dir / filename
        file_path.write_bytes(content)

        meta = self._read_metadata(app_id)
        doc = ApplicationDocument(
            filename=filename,
            size_bytes=len(content),
            content_type="application/pdf" if filename.lower().endswith(".pdf") else "application/octet-stream",
            uploaded_at=datetime.now(timezone.utc),
            has_annotated_version=False,
        )

        docs = [d for d in meta.get("documents", []) if isinstance(d, dict) and d.get("filename") != filename]
        docs.append(doc.model_dump())
        meta["documents"] = docs
        meta["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._write_metadata(app_id, meta)
        return doc

    def mark_documents_indexed(self, app_id: str) -> None:
        app_dir = self.base_path / app_id
        if not app_dir.exists():
            return
        meta = self._read_metadata(app_id)
        docs = []
        for d in meta.get("documents", []):
            if isinstance(d, dict):
                d["is_indexed"] = True
                docs.append(d)
        meta["documents"] = docs
        meta["updated_at"] = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
        self._write_metadata(app_id, meta)


# Singleton
application_service = ApplicationService()
