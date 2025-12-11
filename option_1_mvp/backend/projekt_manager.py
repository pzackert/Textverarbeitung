"""
Projekt Manager
Verwaltet Projekte, Metadaten und Projektstruktur
"""

import uuid
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List


def create_projekt(
    projekt_name: str,
    antragsteller: str,
    modul: str,
    projektart: str,
    beschreibung: Optional[str] = None
) -> str:
    """
    Erstellt neues Projekt im Dateisystem.
    
    Args:
        projekt_name: Name des Projekts
        antragsteller: Name des Unternehmens
        modul: Fördermodul (z.B. "PROFI Standard")
        projektart: Art des Projekts (z.B. "Industrielle Forschung")
        beschreibung: Optionale Projektbeschreibung
        
    Returns:
        projekt_id: Eindeutige ID des Projekts
    """
    
    # 1. Projekt-ID generieren
    projekt_id = f"projekt_{uuid.uuid4().hex[:8]}"
    
    # 2. Verzeichnisstruktur erstellen
    projekt_path = Path(f"data/projects/{projekt_id}")
    projekt_path.mkdir(parents=True, exist_ok=True)
    
    (projekt_path / "uploads").mkdir(exist_ok=True)
    (projekt_path / "extracted").mkdir(exist_ok=True)
    (projekt_path / "results").mkdir(exist_ok=True)
    
    # 3. Metadaten speichern
    metadata = {
        "projekt_id": projekt_id,
        "projekt_name": projekt_name,
        "antragsteller": antragsteller,
        "modul": modul,
        "projektart": projektart,
        "beschreibung": beschreibung,
        "status": "created",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "documents": [],
        "checks_completed": {
            "parsing": False,
            "extraction": False,
            "foerdervoraussetzungen": False,
            "bewertung": False
        }
    }
    
    with open(projekt_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return projekt_id


def load_projekt_metadata(projekt_id: str) -> Dict[str, Any]:
    """Lädt Projekt-Metadaten aus JSON."""
    
    projekt_path = Path(f"data/projects/{projekt_id}")
    metadata_file = projekt_path / "metadata.json"
    
    if not metadata_file.exists():
        raise FileNotFoundError(f"Projekt {projekt_id} nicht gefunden!")
    
    with open(metadata_file, "r", encoding="utf-8") as f:
        return json.load(f)


def update_projekt_metadata(projekt_id: str, updates: Dict[str, Any]) -> None:
    """Aktualisiert Projekt-Metadaten."""
    
    metadata = load_projekt_metadata(projekt_id)
    metadata.update(updates)
    metadata["updated_at"] = datetime.now().isoformat()
    
    projekt_path = Path(f"data/projects/{projekt_id}")
    with open(projekt_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)


def list_projects() -> List[Dict[str, Any]]:
    """Listet alle Projekte auf."""
    projects_dir = Path("data/projects")
    if not projects_dir.exists():
        return []
        
    projects = []
    for p_dir in projects_dir.iterdir():
        if p_dir.is_dir() and (p_dir / "metadata.json").exists():
            try:
                with open(p_dir / "metadata.json", "r", encoding="utf-8") as f:
                    projects.append(json.load(f))
            except Exception:
                continue
                
    # Sort by updated_at desc
    projects.sort(key=lambda x: x.get("updated_at", ""), reverse=True)
    return projects


def delete_projekt(projekt_id: str) -> bool:
    """Löscht ein Projekt und alle zugehörigen Daten."""
    import shutil
    
    projekt_path = Path(f"data/projects/{projekt_id}")
    if not projekt_path.exists():
        return False
        
    try:
        shutil.rmtree(projekt_path)
        return True
    except Exception:
        return False
