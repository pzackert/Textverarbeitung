"""Helpers that connect the Streamlit UI with backend processing."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, TYPE_CHECKING

from backend.core.criteria import check_all_criteria
from backend.dokument_manager import save_document
from backend.parsers.parser import parse_document
from backend.projekt_manager import update_projekt_metadata
from backend.rag.chunker import chunk_text
from backend.utils.logger import setup_logger

from frontend.services import project_service

if TYPE_CHECKING:  # pragma: no cover - import for typing only
    from backend.llm.lm_studio_client import LMStudioClient as _LMStudioClient
    from backend.rag.vector_store import VectorStore as _VectorStore

try:  # pragma: no cover - heavy deps may be missing in tests
    from backend.llm.lm_studio_client import LMStudioClient as _RuntimeLMClient
    _LLM_IMPORT_ERROR: Optional[Exception] = None
except Exception as exc:  # pragma: no cover - defensive
    _RuntimeLMClient = None
    _LLM_IMPORT_ERROR = exc

try:  # pragma: no cover - heavy deps may be missing in tests
    from backend.rag.vector_store import VectorStore as _RuntimeVectorStore
    _VECTOR_STORE_IMPORT_ERROR: Optional[Exception] = None
except Exception as exc:  # pragma: no cover - defensive
    _RuntimeVectorStore = None
    _VECTOR_STORE_IMPORT_ERROR = exc

logger = setup_logger(__name__)

PROJECTS_DIR = Path("data/projects")
PROJECTS_DIR.mkdir(parents=True, exist_ok=True)


def _project_dir(project_id: str) -> Path:
    project_path = PROJECTS_DIR / project_id
    project_path.mkdir(parents=True, exist_ok=True)
    (project_path / "uploads").mkdir(exist_ok=True)
    return project_path


def _build_vector_store():
    if _RuntimeVectorStore is None:
        raise RuntimeError(_VECTOR_STORE_IMPORT_ERROR or RuntimeError("VectorStore nicht verfuegbar"))
    return _RuntimeVectorStore()


def _build_llm_client():
    if _RuntimeLMClient is None:
        raise RuntimeError(_LLM_IMPORT_ERROR or RuntimeError("LLM-Client nicht verfuegbar"))
    return _RuntimeLMClient()


def _get_project_collection(store: Any, project_id: str):
    collection_name = f"project_{project_id}"
    try:
        collection = store.client.get_collection(collection_name)
    except Exception:
        collection = store.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )
    return collection


def handle_document_upload(
    project_id: str,
    doc_type: str,
    uploaded_file: Any,
) -> Dict[str, Any]:
    """Persist, parse and index an uploaded document."""

    try:
        uploaded_file.seek(0)
    except Exception:
        pass

    try:
        doc_entry = save_document(
            project_id,
            doc_type,
            uploaded_file,
            getattr(uploaded_file, "name", f"{doc_type}.bin"),
        )
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Dokumentspeicherung fehlgeschlagen")
        return {"ok": False, "message": f"Dokument konnte nicht gespeichert werden: {exc}"}

    project_path = _project_dir(project_id)
    file_path = project_path / "uploads" / doc_entry["filename"]

    try:
        parse_result = parse_document(file_path)
    except Exception as exc:  # pragma: no cover - defensive
        logger.exception("Parsing fehlgeschlagen")
        return {"ok": False, "message": f"Parsing fehlgeschlagen: {exc}"}

    if parse_result.get("error"):
        return {"ok": False, "message": parse_result["error"]}

    text = parse_result.get("text", "")
    chunks = chunk_text(text)

    indexing_warning: Optional[str] = None
    if chunks:
        try:
            store = _build_vector_store()
            store.collection = _get_project_collection(store, project_id)
            ids = [
                f"{project_id}_{doc_type}_{idx}"
                for idx in range(len(chunks))
            ]
            metadatas = [
                {
                    "doc_type": doc_type,
                    "chunk": idx,
                    "filename": doc_entry["filename"],
                }
                for idx in range(len(chunks))
            ]
            store.add_documents(chunks, metadatas, ids)
        except Exception as exc:  # pragma: no cover - depends on env
            logger.warning("Indexierung deaktiviert: %s", exc)
            indexing_warning = str(exc)

    text_path = project_path / f"document_{doc_type}.txt"
    text_path.write_text(text)

    combined_path = project_path / "document_text.txt"
    combined_texts = []
    for candidate in sorted(project_path.glob("document_*.txt")):
        combined_texts.append(candidate.read_text())
    combined_path.write_text("\n\n".join(combined_texts))

    record = project_service.get_project(project_id)
    required_status = project_service.required_documents_status(record)
    has_all_required = bool(required_status and all(required_status.values()))

    new_status = "uploaded" if has_all_required else "uploading"
    new_step = 3 if has_all_required else 2
    update_fields = {
        "status": new_status,
        "current_step": new_step,
        "last_upload_at": datetime.now().isoformat(),
    }
    update_projekt_metadata(project_id, update_fields)

    response: Dict[str, Any] = {
        "ok": True,
        "doc_entry": doc_entry,
        "chunks": len(chunks),
        "metadata": update_fields,
    }
    if indexing_warning:
        response["warning"] = indexing_warning
    return response


def run_criteria_check(project_id: str) -> Dict[str, Any]:
    """Trigger the end-to-end criteria evaluation pipeline."""

    project_path = _project_dir(project_id)
    text_sources = sorted(project_path.glob("document_*.txt"))
    document_text = "\n\n".join(
        path.read_text() for path in text_sources if path.exists()
    )
    fallback_file = project_path / "document_text.txt"
    if not document_text and fallback_file.exists():
        document_text = fallback_file.read_text()

    if not document_text:
        return {"ok": False, "message": "Keine geparsten Dokumente gefunden."}

    update_projekt_metadata(
        project_id,
        {"status": "checking", "current_step": 3},
    )

    try:
        llm_client = _build_llm_client()
    except Exception as exc:  # pragma: no cover - depends on env
        logger.exception("LLM-Client konnte nicht initialisiert werden")
        return {"ok": False, "message": f"LLM-Client Fehler: {exc}"}

    try:
        vector_store = _build_vector_store()
        vector_store.collection = _get_project_collection(vector_store, project_id)
    except Exception as exc:  # pragma: no cover - depends on env
        logger.exception("VectorStore konnte nicht initialisiert werden")
        return {"ok": False, "message": f"VectorStore Fehler: {exc}"}

    results = check_all_criteria(document_text, llm_client, vector_store)

    (project_path / "results.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False)
    )
    update_projekt_metadata(
        project_id,
        {
            "status": "checked",
            "current_step": 4,
            "result": results.get("overall"),
            "last_check_at": datetime.now().isoformat(),
        },
    )
    return {"ok": True, "results": results}
