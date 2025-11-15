"""PDF Parser - Einfache Text-Extraktion mit PyMuPDF"""
from pathlib import Path
from typing import Dict, Any
import pymupdf
from backend.parsers.base_parser import BaseParser
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


class PDFParser(BaseParser):
    def parse(self, file_path: Path) -> Dict[str, Any]:
        try:
            with pymupdf.open(file_path) as doc:
                text = ""
                for page_num in range(len(doc)):
                    page = doc[page_num]
                    text += page.get_text()
                metadata = {"pages": len(doc), "file_size": file_path.stat().st_size}
                logger.info(f"✓ PDF geparst: {file_path.name} ({metadata['pages']} Seiten)")
                return {"text": text, "metadata": metadata, "error": None}
        except Exception as e:
            logger.error(f"PDF Parse Error: {file_path.name} - {e}")
            return {"text": "", "metadata": {}, "error": str(e)}


if __name__ == "__main__":
    # Test
    print("PDF Parser Test - Bitte eine PDF-Datei in data/input/ ablegen")
    
    # Beispiel-Test mit einer vorhandenen PDF (falls vorhanden)
    test_dir = Path(__file__).parent.parent.parent / "data" / "input"
    test_dir.mkdir(parents=True, exist_ok=True)
    
    pdf_files = list(test_dir.glob("*.pdf"))
    
    if pdf_files:
        parser = PDFParser()
        result = parser.parse(pdf_files[0])
        
        print(f"\n✓ Test erfolgreich!")
        print(f"  Datei: {result['metadata']['filename']}")
        print(f"  Seiten: {result['metadata'].get('page_count', 'N/A')}")
        print(f"  Zeichen: {len(result['text'])}")
        print(f"  Fehler: {result['error']}")
        
        if result['text']:
            print(f"\n  Erste 200 Zeichen:")
            print(f"  {result['text'][:200]}...")
    else:
        print(f"  Keine PDF-Dateien in {test_dir} gefunden")
        print(f"  Bitte eine Test-PDF ablegen und erneut ausführen")
