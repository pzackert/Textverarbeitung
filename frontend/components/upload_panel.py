"""Upload workflow for required project documents."""
from __future__ import annotations

from typing import Dict, List, Optional

import streamlit as st

from frontend.components.toast import show_toast
from frontend.services import process_service, project_service
from frontend.state import session_keys


def _trigger_rerun() -> None:
    try:
        st.rerun()
    except AttributeError:  # pragma: no cover - legacy versions
        st.experimental_rerun()


def _document_label(doc: Dict[str, str]) -> str:
    base = doc.get("label") or doc.get("name") or doc.get("type") or "Dokument"
    return base + (" (erforderlich)" if doc.get("required") else "")


def render_upload_panel(record: Optional[project_service.ProjectRecord]) -> None:
    """Render drag-and-drop upload controls for each configured document type."""

    session_keys.ensure_defaults()
    if not record:
        st.info("Bitte waehle zuerst ein Projekt aus der Sidebar aus.")
        return

    required_docs = project_service.get_required_documents()
    if not required_docs:
        st.warning("Kein Dokumentenkatalog gefunden. Bitte config/criteria_catalog.json pruefen.")
        return

    status = project_service.required_documents_status(record)
    st.caption("Upload-Zwischenstand basiert auf dem Kriterienkatalog.")

    for doc in required_docs:
        doc_type = doc.get("type") or "custom"
        label = _document_label(doc)
        uploaded = status.get(doc_type, False)
        default_open = doc.get("required") and not uploaded
        with st.expander(label, expanded=bool(default_open)):
            st.write(
                "Status:", "Bereit" if uploaded else "Offen",
            )
            with st.form(f"upload-form-{record.id}-{doc_type}"):
                help_text = doc.get("description") or "Datei aus dem Projektordner waehlen."
                file = st.file_uploader(
                    help_text,
                    type=doc.get("extensions"),
                    accept_multiple_files=False,
                    key=f"uploader-{record.id}-{doc_type}",
                )
                col_submit, col_meta = st.columns([1, 1])
                submitted = col_submit.form_submit_button("Upload starten", use_container_width=True)
                if submitted:
                    if not file:
                        col_submit.warning("Bitte zuerst eine Datei auswahlen.")
                    else:
                        file.seek(0)
                        with st.spinner("Dokument wird analysiert..."):
                            result = process_service.handle_document_upload(record.id, doc_type, file)
                        if result.get("ok"):
                            session_keys.push_log(
                                f"{doc_type} erfolgreich verarbeitet ({result.get('chunks', 0)} Chunks)",
                            )
                            warning = result.get("warning")
                            if warning:
                                col_meta.warning(f"Indexierung eingeschraenkt: {warning}")
                            show_toast(f"{label} hochgeladen.", tone="success")
                            _trigger_rerun()
                        else:
                            message = result.get("message", "Unbekannter Fehler")
                            col_submit.error(message)
                            session_keys.push_log(f"Upload fehlgeschlagen: {message}")

    st.markdown("#### Bereits hochgeladene Dokumente")
    if not record.documents:
        st.info("Noch keine Dokumente gespeichert.")
        return

    doc_rows: List[Dict[str, str]] = []
    for doc in record.documents:
        doc_rows.append(
            {
                "Typ": doc.get("doc_type", "-"),
                "Datei": doc.get("original_filename") or doc.get("filename"),
                "Upload": (doc.get("uploaded_at") or "-")[:19].replace("T", " "),
                "Groesse": f"{int(doc.get('file_size', 0)) // 1024} KB",
            }
        )
    st.dataframe(doc_rows, use_container_width=True, hide_index=True)
