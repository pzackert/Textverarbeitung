"""
Document Parser Manager
Vereint alle Parser und bietet einheitliche Schnittstelle
"""
from pathlib import Path
from typing import Dict, Any, List
from backend.parsers.pdf_parser import PDFParser
from backend.parsers.docx_parser import DOCXParser
from backend.parsers.xlsx_parser import XLSXParser
from backend.utils.logger import setup_logger
from backend.utils.config import get_config_value

logger = setup_logger(__name__)


class DocumentParser:
    """
    Zentrale Klasse für Dokumenten-Parsing
    Wählt automatisch den richtigen Parser basierend auf Dateityp
    """
    
    def __init__(self):
        """Initialisiere Parser"""
        self.parsers = {
            '.pdf': PDFParser(),
            '.docx': DOCXParser(),
            '.xlsx': XLSXParser()
        }
        
        # Erlaubte Extensions aus Config
        self.allowed_extensions = get_config_value(
            'parsing.allowed_extensions',
            ['pdf', 'docx', 'xlsx']
        )
        self.max_file_size_mb = get_config_value('parsing.max_file_size_mb', 50)
    
    def is_supported(self, file_path: Path) -> bool:
        """
        Prüfe ob Dateiformat unterstützt wird
        
        Args:
            file_path: Pfad zur Datei
        
        Returns:
            True wenn unterstützt, False sonst
        """
        extension = file_path.suffix.lower()
        return extension.lstrip('.') in self.allowed_extensions
    
    def validate_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Validiere Datei (Format, Größe, Existenz)
        
        Args:
            file_path: Pfad zur Datei
        
        Returns:
            Dictionary mit valid (bool) und error (str)
        """
        # Existenz prüfen
        if not file_path.exists():
            return {
                "valid": False,
                "error": f"Datei nicht gefunden: {file_path}"
            }
        
        # Format prüfen
        if not self.is_supported(file_path):
            supported = ", ".join(self.allowed_extensions)
            return {
                "valid": False,
                "error": f"Dateiformat nicht unterstützt. Erlaubt: {supported}"
            }
        
        # Größe prüfen
        size_mb = file_path.stat().st_size / (1024 * 1024)
        if size_mb > self.max_file_size_mb:
            return {
                "valid": False,
                "error": f"Datei zu groß: {size_mb:.2f} MB (Max: {self.max_file_size_mb} MB)"
            }
        
        return {"valid": True, "error": None}
    
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse Dokument mit passendem Parser
        
        Args:
            file_path: Pfad zur Datei
        
        Returns:
            Parse-Ergebnis (text, metadata, error)
        """
        # Validierung
        validation = self.validate_file(file_path)
        if not validation["valid"]:
            logger.error(f"✗ Validierung fehlgeschlagen: {validation['error']}")
            return {
                "text": "",
                "metadata": {},
                "error": validation["error"]
            }
        
        # Richtigen Parser wählen
        extension = file_path.suffix.lower()
        parser = self.parsers.get(extension)
        
        if parser is None:
            error_msg = f"Kein Parser für {extension} verfügbar"
            logger.error(f"✗ {error_msg}")
            return {
                "text": "",
                "metadata": {},
                "error": error_msg
            }
        
        # Parsen
        logger.info(f"Parse {file_path.name} mit {parser.__class__.__name__}")
        return parser.parse(file_path)
    
    def parse_multiple(self, file_paths: List[Path]) -> List[Dict[str, Any]]:
        """
        Parse mehrere Dokumente
        
        Args:
            file_paths: Liste von Dateipfaden
        
        Returns:
            Liste von Parse-Ergebnissen
        """
        results = []
        for file_path in file_paths:
            result = self.parse(file_path)
            results.append(result)
        return results


if __name__ == "__main__":
    # Test
    print("\n=== Document Parser Test ===\n")
    
    parser = DocumentParser()
    
    # Test-Verzeichnis
    test_dir = Path(__file__).parent.parent.parent / "data" / "input"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    # Finde alle unterstützten Dateien
    supported_files = []
    for ext in parser.allowed_extensions:
        supported_files.extend(test_dir.glob(f"*.{ext}"))
    
    if supported_files:
        print(f"Gefundene Dateien: {len(supported_files)}\n")
        
        for file_path in supported_files:
            result = parser.parse(file_path)
            
            print(f"Datei: {result['metadata'].get('filename', 'Unknown')}")
            print(f"  Typ: {result['metadata'].get('file_type', 'Unknown')}")
            print(f"  Größe: {result['metadata'].get('size_mb', 0)} MB")
            print(f"  Zeichen: {len(result['text'])}")
            print(f"  Fehler: {result['error']}")
            print()
    else:
        print(f"Keine Test-Dateien in {test_dir} gefunden")
        print(f"Unterstützte Formate: {', '.join(parser.allowed_extensions)}")
        print("\nBitte Test-Dateien ablegen und erneut ausführen")
