"""
Base Parser für alle Dokumenttypen
Option 1: Einfache Parser ohne komplexe Struktur-Extraktion
"""
from abc import ABC, abstractmethod
from typing import Dict, Any
from pathlib import Path


class BaseParser(ABC):
    """
    Basis-Klasse für alle Parser
    Einfache Struktur ohne komplexe Features (OPTION 1)
    """
    
    @abstractmethod
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse Dokument und extrahiere Text
        
        Args:
            file_path: Pfad zur Datei
        
        Returns:
            Dictionary mit:
                - text: Extrahierter Text
                - metadata: Basis-Metadaten (Dateiname, Typ, Größe)
                - error: Fehler falls aufgetreten (optional)
        """
        pass
    
    def get_metadata(self, file_path: Path) -> Dict[str, Any]:
        """
        Extrahiere Basis-Metadaten
        
        Args:
            file_path: Pfad zur Datei
        
        Returns:
            Metadaten-Dictionary
        """
        stat = file_path.stat()
        return {
            "filename": file_path.name,
            "file_type": file_path.suffix.lower(),
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2)
        }
