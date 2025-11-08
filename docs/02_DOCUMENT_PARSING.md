# Document Parsing
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 8. November 2025

## Übersicht

Framework zur Extraktion und Verarbeitung von Dokumenteninhalten für die LLM-Analyse.

## Unterstützte Formate

### PDF (*.pdf)
- Textextraktion
- OCR für Scans
- Tabellenextraktion
- Metadaten

### Word (*.docx, *.doc)
- Volltext mit Formatierung
- Tabellen
- Eingebettete Objekte

### Excel (*.xlsx, *.xls)
- Tabellenextraktion
- Formelauswertung
- Multi-Sheet-Handling

### Text (*.txt, *.md)
- UTF-8 Encoding
- Markdown-Parsing
- Strukturerkennung

## Verarbeitung

### Ablauf
1. Dateityp erkennen
2. Passenden Processor wählen
3. Inhalt extrahieren
4. Normalisieren
5. JSON ausgeben

### Output-Format
```json
{
    "metadata": {
        "filename": "example.pdf",
        "type": "pdf",
        "pages": 5
    },
    "content": {
        "text": "Extrahierter Text...",
        "tables": [],
        "structure": {}
    }
}
```

## Technische Details

### Libraries
- PyPDF2/pdf2image für PDF
- python-docx für Word
- pandas für Excel
- Standard-Lib für Text

### Optimierungen
- Parallel Processing
- Caching
- Fehlerbehandlung

## Sicherheit
- Virus-Scan
- Größenlimits
- Sandbox-Ausführung