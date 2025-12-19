# Dokumentenparsing
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 3.0 (Option 1 MVP + Future Features)  
**Stand:** 13. November 2025

---

## 🎯 GRUNDLEGENDES ZIEL

Wir bauen ein optimales RAG-System (Retrieval-Augmented Generation), das Dokumente der IFB Hamburg intelligent verarbeitet.

> **Docling-Migration (Dez 2025)**
> - Docling + Docling-Core sind die einzige Parsing-Quelle (PDF, DOCX, XLSX). PyMuPDF/python-docx/openpyxl entfallen.
> - Jeder Chunk trägt Bounding Box + `page_width`/`page_height` (Frontend kann Zoom-sicher highlighten).
> - Tabellen bleiben strukturiert (Markdown aus Docling) und werden als eigene Blöcke persistiert.
> - Hybrid Chunking: Docling-Blöcke zuerst, zu große Blöcke werden sekundär gesplittet; BBox wird geerbt.
> - ChromaDB wird mit neuem Metadaten-Schema (`schema_version=docling-v1`) frisch angelegt.

### ✅ OPTION 1 (MVP - Super-Lite):
Das System extrahiert den **Volltext** aus allen relevanten Dokumenten. Jedes Dokument wird vollständig erfasst und für RAG vorbereitet.

**Fokus Option 1:**
- Nur Text-Extraktion (kein Structure Parsing)
- Einfache Funktionen (keine komplexe OOP-Architektur)
- Drei Formate: PDF, DOCX, XLSX
- Direkter Zugriff mit Libraries

### ⚠️ OPTION 2+ (Advanced Features):
- Strukturerkennung (Überschriften, Absätze, Listen)
- Tabellen-Extraktion mit Kontext
- Formularfeld-Erkennung
- OCR-Funktionalität
- Parallelverarbeitung
- Caching-System

---

## 📄 UNTERSTÜTZTE DOKUMENTFORMATE

Das System unterstützt initial die drei wichtigsten Formate:

### PDF-Dokumente (*.pdf) - ✅ OPTION 1

**Verwendung:** Projektskizze, Projektantrag, Förderrichtlinien

**Features Option 1 (MVP):**
- ✅ Vollständige Textextraktion mit PyMuPDF
- ✅ Einfache Metadaten (Autor, Datum falls vorhanden)

**⚠️ Features Option 2+:**
- Strukturerkennung (Überschriften, Absätze, Listen)
- Tabellen-Extraktion
- Layout-Analyse

### Word-Dokumente (*.docx) - ✅ OPTION 1

**Verwendung:** Projektskizze, Projektantrag

**Features Option 1 (MVP):**
- ✅ Volltext-Extraktion mit python-docx
- ✅ Basis-Metadaten

**⚠️ Features Option 2+:**
- Formularfeld-Erkennung (Key-Value-Paare)
- Tabellen-Extraktion
- Dokumentenhierarchie (Kapitel, Unterkapitel)

### Excel-Dateien (*.xlsx, *.xls) - ✅ OPTION 1

**Verwendung:** Checklisten, Bewertungstabellen, Projektkalkulation

**Features Option 1 (MVP):**
- ✅ Text aus Zellen extrahieren mit openpyxl
- ✅ Einfache Konvertierung zu Text

**⚠️ Features Option 2+:**
- Intelligente Tabellen-zu-Text-Konvertierung
- Spaltenüberschriften-Verknüpfung
- Multi-Sheet-Support mit Kontext
- Formeln und Berechnungen

### ⚠️ OCR-Funktionalität - OPTION 2+

**Zukünftige Erweiterung:**
- Tesseract OCR Integration
- Bildqualitäts-Optimierung
- Layout-Analyse für strukturierte Extraktion

---

## 🗂️ DOKUMENT-TYPEN

### 1. Projektskizze
**Umfang:** 2-3 Seiten  
**Format:** PDF oder DOCX

**Inhalt:**
- Ansprechpartner (Liste)
- Unternehmensbeschreibung
- Technologischer Lösungsansatz
- Marktpotenzial und Vermarktung
- Projektumfang

**Parsing-Strategie:** Volltext-Extraktion mit Abschnittserkennung

### 2. Projektantrag (Formular)
**Umfang:** Mehrseitiges Formular + Anhänge  
**Format:** PDF oder DOCX

**Pflichtdokumente:**
- Projektbeschreibung (Formularfelder)
- Projektkalkulation (Excel)
- KMU-Erklärung (PDF)
- Jahresabschlüsse (2x PDF)
- Handelsregisterauszug (PDF)
- Finanz- und Arbeitsplatzübersicht (Excel)

**Optional:**
- Lebensläufe (PDF)
- Letters of Intent (PDF)

**Parsing-Strategie:** Formularfelder als Key-Value-Paare + Volltext

---

## 🔄 EXTRAKTIONS-STRATEGIE

### ✅ OPTION 1 (MVP - Super-Lite):

Bei jedem Dokument extrahieren wir **nur den Volltext**:

**Ausgabe Option 1:**
```json
{
  "volltext": "Kompletter Dokumententext...",
  "metadaten": {
    "dokumenttyp": "projektskizze",
    "dateiname": "projektskizze.pdf",
    "dateigröße_mb": 2.4
  }
}
```

**Einfache Python-Funktion (Konzept):**
```python
def extract_text_simple(file_path: Path) -> dict:
    """Einfache Textextraktion für Option 1"""
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        text = extract_pdf_text(file_path)  # PyMuPDF
    elif suffix == '.docx':
        text = extract_docx_text(file_path)  # python-docx
    elif suffix in ['.xlsx', '.xls']:
        text = extract_excel_text(file_path)  # openpyxl
    else:
        raise ValueError(f"Nicht unterstütztes Format: {suffix}")
    
    return {
        "volltext": text,
        "metadaten": {
            "dokumenttyp": detect_doc_type(file_path.name),
            "dateiname": file_path.name,
            "dateigröße_mb": file_path.stat().st_size / (1024*1024)
        }
    }
```

---

### ⚠️ OPTION 2+ (Advanced Extraction):

Zusätzlich zur Textextraktion:

**1. Strukturdaten**
Überschriften, Kapitelnummern, Paragraphen, Listen und Tabellen werden als solche erkannt.

**Ausgabe:**
```json
{
  "struktur": {
    "kapitel": [
      {
        "nummer": "1",
        "titel": "Einleitung",
        "absätze": ["Absatz 1...", "Absatz 2..."]
      }
    ],
    "tabellen": [
      {
        "name": "Kostenübersicht",
        "rows": [...]
      }
    ]
  }
}
```

**2. Erweiterte Metadaten**
```json
{
  "metadaten": {
    "dokumenttyp": "projektskizze",
    "erstellt_am": "2025-03-15",
    "version": "1.2",
    "autor": "Mustermann GmbH",
    "programm": "PROFI Standard",
    "seiten": 3
  }
}
```

---

## 🏗️ MODULARE ARCHITEKTUR

### ✅ OPTION 1 (MVP - Einfache Funktionen):

**Keine OOP-Architektur, nur einfache Funktionen:**

```python
from pathlib import Path
from typing import Dict, Any

def parse_document(file_path: Path) -> Dict[str, Any]:
    """Hauptfunktion für Dokumentenparsing"""
    suffix = file_path.suffix.lower()
    
    if suffix == '.pdf':
        return parse_pdf_simple(file_path)
    elif suffix == '.docx':
        return parse_docx_simple(file_path)
    elif suffix in ['.xlsx', '.xls']:
        return parse_excel_simple(file_path)
    else:
        raise ValueError(f"Format nicht unterstützt: {suffix}")

# Keine Factory-Pattern, keine BaseParser-Klasse
# Nur direkte, einfache Funktionen
```

---

### ⚠️ OPTION 2+ (Modulare OOP-Architektur):

Der Code wird strikt modular aufgebaut mit klarer Trennung der Verantwortlichkeiten:

```
DocumentProcessor (Hauptkoordinator)
├── FormatDetector (erkennt Dateityp)
├── ParserFactory (wählt richtigen Parser)
├── Parser-Module
│   ├── PDFParser
│   ├── WordParser  
│   ├── ExcelParser
│   └── BaseParser (Fallback)
├── TextProcessor (Bereinigung, Normalisierung)
├── ChunkGenerator (intelligente Textaufteilung)
└── VectorStore (ChromaDB-Integration)
```

**Parser-Schnittstelle:**

Jeder Parser implementiert dieselbe Schnittstelle mit drei Kernmethoden:

```python
class BaseParser(ABC):
    """Basis-Interface für alle Parser."""
    
    @abstractmethod
    def extract_text(self, file_path: Path) -> str:
        """Holt den Rohtext."""
        pass
    
    @abstractmethod
    def extract_structure(self, file_path: Path) -> dict:
        """Erkennt Dokumentstruktur."""
        pass
    
    @abstractmethod
    def extract_metadata(self, file_path: Path) -> dict:
        """Sammelt Metainformationen."""
        pass
```

**Parser-Factory:**

```python
class ParserFactory:
    """Wählt den richtigen Parser basierend auf Dateityp."""
    
    _parsers = {
        ".pdf": PDFParser,
        ".docx": WordParser,
        ".xlsx": ExcelParser,
        ".xls": ExcelParser
    }
    
    @classmethod
    def get_parser(cls, file_path: Path) -> BaseParser:
        """Gibt passenden Parser zurück."""
        suffix = file_path.suffix.lower()
        parser_class = cls._parsers.get(suffix, BaseParser)
        return parser_class()
    
    @classmethod
    def register_parser(cls, extension: str, parser_class: type):
        """Registriert neuen Parser für Erweiterung."""
        cls._parsers[extension] = parser_class
```

---

## 🔧 ERWEITERBARKEIT ALS KERNPRINZIP - ⚠️ OPTION 2+

Neue Formate werden durch simple Ergänzung unterstützt:

### Schritte zur Erweiterung:

1. **Neuen Parser erstellen** (z.B. `RTFParser`)
   ```python
   class RTFParser(BaseParser):
       def extract_text(self, file_path: Path) -> str:
           # RTF-spezifische Logik
           pass
   ```

2. **Von BaseParser ableiten**
   - Implementiere alle drei Kernmethoden
   - Verwende bewährte Libraries

3. **In ParserFactory registrieren**
   ```python
   ParserFactory.register_parser(".rtf", RTFParser)
   ```

**Der bestehende Code muss nicht modifiziert werden.** Das System erkennt automatisch das neue Format und nutzt den entsprechenden Parser.

---

## 🧩 INTELLIGENTES CHUNKING FÜR CHROMADB

### ✅ OPTION 1 (MVP - Einfaches Chunking):

**Simple Text-Splitting:**

```python
def simple_chunk_text(text: str, chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Einfaches Chunking für Option 1
    Teilt Text in Chunks mit fester Größe und Überlappung
    """
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    
    return chunks
```

**Keine semantischen Grenzen, keine komplexe Logik.**

---

### ⚠️ OPTION 2+ (Intelligentes Chunking):

Dokumente werden intelligent in Chunks aufgeteilt für optimales RAG-Retrieval:

**Chunking-Strategie:**

#### 1. Semantische Grenzen
Wir trennen an Absätzen und Kapiteln, **nicht mitten im Satz**.

```python
chunk_size = 1000  # Zeichen, keine Token-Limit!
chunk_overlap = 200  # 20% Überlappung
separators = ["\n\n", "\n", ". ", " ", ""]
```

#### 2. Kontexterhaltung
Chunks überlappen sich um 20%, damit Zusammenhänge nicht verloren gehen.

**Beispiel:**
```
Chunk 1: "...Ende von Absatz 1. Beginn Absatz 2..."
Chunk 2: "Beginn Absatz 2... Ende Absatz 2. Beginn Absatz 3..."
```

#### 3. Flexible Größe
- Kurze Abschnitte bleiben zusammen
- Lange werden sinnvoll geteilt
- Tabellen bleiben vollständig zusammen

#### 4. Metadaten-Vererbung
Jeder Chunk weiß, aus welchem Dokument, Kapitel und Abschnitt er stammt.

```json
{
  "chunk_id": "chunk_001",
  "text": "Chunk-Inhalt...",
  "metadata": {
    "dokument_id": "projektskizze_001",
    "dokumenttyp": "projektskizze",
    "kapitel": "1. Einleitung",
    "seite": 1,
    "chunk_index": 0
  }
}
```

---

## 🎯 SPEZIALBEHANDLUNG FÜR IFB-DOKUMENTE - ⚠️ OPTION 2+

**In Option 1: Nur einfache Textextraktion, keine Spezialbehandlung.**

**Option 2+ Features:**

### Projektskizzen
**Formularfelder** werden als Key-Value-Paare extrahiert. Die Feldbezeichnung wird mit dem Inhalt verknüpft für präzise Suche.

**Beispiel:**
```json
{
  "formularfelder": {
    "Projektname": "Entwicklung einer KI-gestützten Verpackungsanlage",
    "Antragsteller": "Mustermann GmbH",
    "Projektlaufzeit": "24 Monate",
    "Gesamtkosten": "450.000 EUR"
  }
}
```

### Projektanträge
**Mehrseitige Anträge** behalten ihre Abschnittsstruktur. Anhänge werden erkannt und verlinkt.

**Beispiel:**
```json
{
  "abschnitte": [
    {
      "nummer": "A",
      "titel": "Projektbeschreibung",
      "inhalt": "..."
    },
    {
      "nummer": "B",
      "titel": "Projektkalkulation",
      "anhang": "kalkulation.xlsx"
    }
  ]
}
```

### Checklisten
**Kriterien und Bewertungen** werden strukturiert erfasst. Checkboxen werden in maschinenlesbare Ja/Nein-Werte übersetzt.

**Beispiel:**
```json
{
  "kriterien": [
    {
      "id": "K001",
      "beschreibung": "Betriebsstätte in Hamburg",
      "status": true,
      "bewertung": "erfüllt"
    }
  ]
}
```

---

## ✅ QUALITÄTSSICHERUNG

### ✅ OPTION 1 (Basis-Qualitätssicherung):

**UTF-8 überall:**
Deutsche Umlaute und Sonderzeichen werden korrekt behandelt.

```python
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()
```

**Einfache Fehlerbehandlung:**
```python
try:
    text = parse_document(file_path)
except Exception as e:
    print(f"Fehler beim Parsen: {e}")
    text = ""
```

---

### ⚠️ OPTION 2+ (Erweiterte Qualitätssicherung):

**Fehlertoleranz:**
Beschädigte Dokumente führen nicht zum Absturz. Der Parser extrahiert, was möglich ist, und loggt Probleme.

```python
try:
    text = parser.extract_text(file_path)
except ParsingError as e:
    logger.warning(f"Parsing-Fehler in {file_path}: {e}")
    text = parser.extract_partial_text(file_path)
```

**Vollständigkeitsprüfung:**
Nach dem Parsing wird verifiziert, dass kein Inhalt verloren ging.

```python
def verify_completeness(original_file: Path, extracted_text: str) -> bool:
    """Prüft, ob Extraktion vollständig ist."""
    original_size = original_file.stat().st_size
    extracted_size = len(extracted_text.encode('utf-8'))
    
    # Warnung bei großer Diskrepanz
    if extracted_size < original_size * 0.5:
        logger.warning(f"Nur {extracted_size}/{original_size} Bytes extrahiert")
        return False
    
    return True
```

---

## 🛠️ TECHNISCHE UMSETZUNG

### ✅ OPTION 1 - Verwendete Libraries:

**PyMuPDF (fitz)** für PDF-Verarbeitung
- Schnell und zuverlässig
- Vollständige Textextraktion
```bash
pip install PyMuPDF
```

**python-docx** für Word-Dokumente
- Native DOCX-Unterstützung
```bash
pip install python-docx
```

**openpyxl** für Excel-Files
- Vollständige Format-Unterstützung
```bash
pip install openpyxl
```

**ChromaDB** als lokale Vektor-Datenbank
- Embedding-Speicherung
- Similarity-Search
```bash
pip install chromadb
```

**sentence-transformers** für Embeddings
- Multilingual support
```bash
pip install sentence-transformers
```

**Streamlit** für UI
```bash
pip install streamlit
```

---

### ⚠️ OPTION 2+ - Zusätzliche Libraries:

**langchain** als Orchestrierung für das RAG-System
- Text-Splitting
- Embedding-Integration
- Vector-Store-Anbindung
```bash
pip install langchain
```

---

### Code-Dokumentation - ✅ OPTION 1

Der Code wird mit **Docstrings** dokumentiert. Jede Funktion erklärt ihre Parameter und Rückgabewerte.

**Beispiel:**
```python
def parse_document(file_path: Path) -> dict:
    """
    Parst ein Dokument und extrahiert Text.
    
    Args:
        file_path: Pfad zur Datei (PDF, DOCX oder XLSX)
    
    Returns:
        dict mit volltext und metadaten
    
    Example:
        >>> result = parse_document(Path("projektskizze.pdf"))
        >>> print(result["volltext"][:100])
    """
    pass
```

---

## ⚡ PERFORMANCE-OPTIMIERUNG - ⚠️ OPTION 2+

**In Option 1: Keine Parallelverarbeitung, kein Caching, keine Batch-Operationen.**

**Option 2+ Features:**

### Parallelverarbeitung
Mehrere Dokumente werden gleichzeitig geparst (multiprocessing).

```python
from multiprocessing import Pool

def parse_documents_parallel(file_paths: list[Path]) -> list[ParseResult]:
    """Parst mehrere Dokumente parallel."""
    with Pool(processes=4) as pool:
        results = pool.map(parse_document, file_paths)
    return results
```

### Caching
Bereits verarbeitete Dokumente werden markiert und nicht erneut geparst.

```python
def is_cached(file_path: Path) -> bool:
    """Prüft, ob Dokument bereits geparst wurde."""
    cache_file = get_cache_path(file_path)
    return cache_file.exists()

def load_from_cache(file_path: Path) -> ParseResult:
    """Lädt geparstes Ergebnis aus Cache."""
    cache_file = get_cache_path(file_path)
    with open(cache_file, "r", encoding="utf-8") as f:
        return ParseResult.from_json(f.read())
```

### Batch-Operationen
Embeddings werden in Gruppen generiert für bessere Effizienz.

```python
def generate_embeddings_batch(chunks: list[str], batch_size: int = 100):
    """Generiert Embeddings in Batches."""
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]
        embeddings = embedding_model.embed(batch)
        yield embeddings
```

---

## 📊 ERWARTETES ERGEBNIS

### ✅ OPTION 1 (MVP):

Nach dem Parsing haben wir:

✅ **Vollständigen, durchsuchbaren Text** aller Dokumente  
✅ **Basis-Metadaten** (Dateiname, Typ)
✅ **Einfache Chunks** für RAG-Retrieval  

**Beispiel-Output Option 1:**

```json
{
  "volltext": "Kompletter Text der Projektskizze...",
  "metadaten": {
    "dateiname": "projektskizze.pdf",
    "dokumenttyp": "projektskizze",
    "dateigröße_mb": 2.4
  },
  "chunks": [
    "Chunk 1 Inhalt...",
    "Chunk 2 Inhalt...",
    "Chunk 3 Inhalt..."
  ]
}
```

---

### ⚠️ OPTION 2+ (Erweitert):

✅ **Strukturierte Metadaten** für präzise Filterung  
✅ **Intelligente Chunks** mit Kontext
✅ **Erweiterbare Codebasis** für zukünftige Anforderungen  

**Beispiel-Output Option 2+:**

```json
{
  "dokument_id": "projektskizze_001",
  "dokumenttyp": "projektskizze",
  "volltext": "Kompletter Text der Projektskizze...",
  "struktur": {
    "kapitel": [...],
    "tabellen": [...]
  },
  "metadaten": {
    "dateiname": "projektskizze.pdf",
    "erstellt_am": "2025-03-15",
    "seiten": 3
  },
  "chunks": [
    {
      "chunk_id": "chunk_001",
      "text": "Chunk 1 Inhalt...",
      "metadata": {...}
    }
  ],
  "vector_ids": ["vec_001", "vec_002", ...]
}
```

---

## 🎓 ANWENDUNGSBEISPIEL - ✅ OPTION 1 + ⚠️ OPTION 2+

**Funktioniert in beiden Optionen:**

Das System ermöglicht es, Fragen wie:

**"Welche Voraussetzungen hat das PROFI-Programm?"**  
→ RAG findet relevante Textstellen aus Förderrichtlinien

**"Was steht in der Projektskizze zum Thema Innovation?"**  
→ RAG extrahiert Abschnitt "Technologischer Lösungsansatz"

**"Ist das Unternehmen KMU-berechtigt?"**  
→ RAG findet Informationen aus KMU-Erklärung und Jahresabschlüssen

präzise zu beantworten, indem es die relevanten Textstellen aus den geparsten Dokumenten findet und dem LLM zur Verfügung stellt.

---

## 🔐 SICHERHEIT - ⚠️ OPTION 2+

**In Option 1: Nur lokale Verarbeitung, keine erweiterten Sicherheitsfeatures.**

**Option 2+ Features:**

### Datei-Validierung
- Dateityp-Prüfung vor Verarbeitung
- Größenlimits (max. 50 MB pro Datei)
- Virus-Scan (optional integrierbar)

### Sandbox-Ausführung
- Parser laufen in isolierter Umgebung
- Kein Zugriff auf Systemressourcen
- Timeout bei hängenden Operationen

### Datenschutz
- Lokale Verarbeitung (keine Cloud)
- Verschlüsselte Speicherung möglich
- DSGVO-konform

---

*Diese Spezifikation dient als Arbeitsgrundlage für die Implementierung des Dokumentenparsing-Moduls. Jeder Abschnitt kann in konkrete Entwicklungs-Tasks übersetzt werden.*