import json
from pathlib import Path
from datetime import datetime, timezone

from src.api.schemas_application import ApplicationCreate
from src.services.application_service import ApplicationService


def test_list_applications_discovers_folders_without_registry(tmp_path: Path):
    app_id = "proj1"
    uploads = tmp_path / app_id / "uploads"
    uploads.mkdir(parents=True)
    (uploads / "doc.pdf").write_bytes(b"content")

    service = ApplicationService(base_path=str(tmp_path))
    apps = service.list_applications()

    assert len(apps) == 1
    assert apps[0].id == app_id
    assert apps[0].document_count == 1
    assert not (tmp_path / "registry.json").exists()


def test_get_application_reads_metadata_and_docs(tmp_path: Path):
    app_id = "proj2"
    project_dir = tmp_path / app_id
    uploads = project_dir / "uploads"
    annotated = project_dir / "annotated"
    uploads.mkdir(parents=True)
    annotated.mkdir(parents=True)

    (uploads / "file.txt").write_text("hello", encoding="utf-8")
    (annotated / "file_annotated.txt").write_text("annotated", encoding="utf-8")

    meta = {
        "id": app_id,
        "title": "My App",
        "applicant": "ACME",
        "status": "draft",
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "updated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "documents": [{"filename": "file.txt", "is_indexed": True}],
    }
    (project_dir / "metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    service = ApplicationService(base_path=str(tmp_path))
    app = service.get_application(app_id)

    assert app is not None
    assert app.title == "My App"
    assert len(app.documents) == 1
    doc = app.documents[0]
    assert doc.filename == "file.txt"
    assert doc.is_indexed is True
    assert doc.has_annotated_version is True


def test_add_and_mark_indexed_updates_metadata(tmp_path: Path):
    service = ApplicationService(base_path=str(tmp_path))

    created = service.create_application(
        ApplicationCreate(title="New", applicant="User", description=None, funding_request=None)
    )

    doc = service.add_document(created.id, "note.pdf", b"pdf")
    assert doc is not None

    meta_path = tmp_path / created.id / "metadata.json"
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta.get("documents")
    assert meta["documents"][0]["filename"] == "note.pdf"
    assert meta["documents"][0].get("is_indexed") is False

    service.mark_documents_indexed(created.id)
    meta_after = json.loads(meta_path.read_text(encoding="utf-8"))
    assert meta_after["documents"][0].get("is_indexed") is True

    app = service.get_application(created.id)
    assert app.documents[0].is_indexed is True
