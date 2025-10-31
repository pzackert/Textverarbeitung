"""
Base Parser - Abstract Class für alle Dokumenten-Parser
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any


class BaseParser(ABC):
    """Abstract Base Class für alle Parser."""
    
    @abstractmethod
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parst Datei und extrahiert strukturierte Daten.
        
        Args:
            file_path: Pfad zur Datei
            
        Returns:
            {
                "text": str,              # Volltext
                "metadata": dict,         # Titel, Datum, Autor
                "structured_data": dict,  # Strukturierte Felder
                "tables": list[dict]      # Extrahierte Tabellen
            }
        """
        pass
    
    @abstractmethod
    def is_supported(self, file_path: Path) -> bool:
        """Prüft ob Dateiformat unterstützt wird."""
        pass
