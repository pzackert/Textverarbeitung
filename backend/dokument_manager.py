"""
Dokument Manager
Verwaltet hochgeladene Dokumente
"""

import uuid
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, BinaryIO

from backend.projekt_manager import load_projekt_metadata, update_projekt_metadata


def save_document(
    projekt_id: str,
    doc_type: str,
    uploaded_file: BinaryIO,
    original_filename: str
) -> Dict[str, Any]:
    """
    Speichert hochgeladenes Dokument.
    
    Args:
        projekt_id: ID des Projekts
        doc_type: Typ des Dokuments (z.B. "projektskizze")
        uploaded_file: Datei-Objekt
        original_filename: Originaler Dateiname
        
    Returns:
        Document Entry mit Metadaten
    """
    
    # 1. Dateipfad generieren
    projekt_path = Path(f"data/projects/{projekt_id}")
    upload_path = projekt_path / "uploads"
    
    filename = f"{doc_type}_{original_filename}"
    file_path = upload_path / filename
    
    # 2. Datei speichern
    with open(file_path, "wb") as f:
        shutil.copyfileobj(uploaded_file, f)
    
    # 3. Metadaten erstellen
    doc_entry = {
        "doc_id": str(uuid.uuid4()),
        "doc_type": doc_type,
        "filename": filename,
        "original_filename": original_filename,
        "uploaded_at": datetime.now().isoformat(),
        "file_size": file_path.stat().st_size,
        "parsed": False
    }
    
    # 4. Projekt-Metadaten aktualisieren
    metadata = load_projekt_metadata(projekt_id)
    metadata["documents"].append(doc_entry)
    update_projekt_metadata(projekt_id, {"documents": metadata["documents"]})
    
    return doc_entry


def delete_document(projekt_id: str, doc_type: str) -> None:
    """Löscht Dokument aus Projekt."""
    
    metadata = load_projekt_metadata(projekt_id)
    
    # Dokument finden
    doc = next((d for d in metadata["documents"] if d["doc_type"] == doc_type), None)
    if not doc:
        return
    
    # Datei löschen
    file_path = Path(f"data/projects/{projekt_id}/uploads/{doc['filename']}")
    if file_path.exists():
        file_path.unlink()
    
    # Metadaten aktualisieren
    metadata["documents"] = [d for d in metadata["documents"] if d["doc_type"] != doc_type]
    update_projekt_metadata(projekt_id, {"documents": metadata["documents"]})
