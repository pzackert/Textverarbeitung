# Dokumentenparsing
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 2.0  
**Stand:** 10. November 2025

---

## 🎯 GRUNDLEGENDES ZIEL

Wir bauen ein optimales RAG-System (Retrieval-Augmented Generation), das Dokumente der IFB Hamburg intelligent verarbeitet. Das System extrahiert den **kompletten Volltext** aus allen relevanten Dokumenten - **ohne künstliche Token-Beschränkungen**. Jedes Dokument wird vollständig erfasst und in ChromaDB als Vektor-Datenbank gespeichert, damit später präzise Suchanfragen möglich sind.

---

## 📄 UNTERSTÜTZTE DOKUMENTFORMATE

Das System unterstützt initial die drei wichtigsten Formate:

### PDF-Dokumente (*.pdf)
Förderrichtlinien, offizielle Bescheide und Projektskizzen. Hier extrahieren wir den kompletten Text inklusive Strukturinformationen wie Überschriften und Paragraphen.

**Verwendung:** Projektskizze, Projektantrag, Förderrichtlinien

**Features:**
- Vollständige Textextraktion
- Strukturerkennung (Überschriften, Absätze, Listen)
- Tabellen-Extraktion
- Metadaten (Autor, Erstellungsdatum, Version)

### Word-Dokumente (*.docx)
Projektanträge und ausgefüllte Formulare. Der Parser erkennt Formularfelder, extrahiert deren Inhalte strukturiert und behält die Dokumentenhierarchie bei.

**Verwendung:** Projektskizze, Projektantrag

**Features:**
- Volltext mit Formatierung
- Formularfeld-Erkennung (Key-Value-Paare)
- Tabellen-Extraktion
- Dokumentenhierarchie (Kapitel, Unterkapitel)

### Excel-Dateien (*.xlsx, *.xls)
Bewertungstabellen, Checklisten und strukturierte Daten. Tabellen werden intelligent in Text umgewandelt, wobei Spaltenüberschriften und Zellinhalte sinnvoll verknüpft werden.

**Verwendung:** Checklisten, Bewertungstabellen, Projektkalkulation

**Features:**
- Strukturierte Datenextraktion
- Intelligente Tabellen-zu-Text-Konvertierung
- Spaltenüberschriften-Verknüpfung
- Multi-Sheet-Support

### OCR-Funktionalität (Zukünftig)
**OCR-Funktionalität** wird als zukünftige Erweiterung vorbereitet. Der Code wird so strukturiert, dass OCR-Module später nahtlos integriert werden können, um auch gescannte PDFs und Bilddateien zu verarbeiten.

**Geplante Features:**
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

Bei jedem Dokument extrahieren wir **drei Ebenen von Information**:

### 1. Volltext
Der komplette Inhalt **ohne Verluste**. Wir setzen keine künstlichen Grenzen bei der Textlänge. Wenn ein Förderrichtlinien-Dokument 200 Seiten hat, erfassen wir alle 200 Seiten.

**Ausgabe:**
```json
{
  "volltext": "Kompletter Dokumententext ohne Kürzungen..."
}
```

### 2. Strukturdaten
Überschriften, Kapitelnummern, Paragraphen, Listen und Tabellen werden als solche erkannt und markiert. Diese Struktur hilft später bei der gezielten Suche.

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

### 3. Metadaten
Dokumenttyp, Erstellungsdatum, Version, Autor und Programmzugehörigkeit (PROFI, etc.) werden separat gespeichert für effiziente Filterung.

**Ausgabe:**
```json
{
  "metadaten": {
    "dokumenttyp": "projektskizze",
    "erstellt_am": "2025-03-15",
    "version": "1.2",
    "autor": "Mustermann GmbH",
    "programm": "PROFI Standard",
    "seiten": 3,
    "dateigröße": "2.4 MB"
  }
}
```

---

## 🏗️ MODULARE ARCHITEKTUR

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

### Parser-Schnittstelle

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

### Parser-Factory

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

## 🔧 ERWEITERBARKEIT ALS KERNPRINZIP

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

Dokumente werden intelligent in Chunks aufgeteilt für optimales RAG-Retrieval:

### Chunking-Strategie

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

## 🎯 SPEZIALBEHANDLUNG FÜR IFB-DOKUMENTE

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

### UTF-8 überall
Deutsche Umlaute und Sonderzeichen werden korrekt behandelt.

```python
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()
```

### Fehlertoleranz
Beschädigte Dokumente führen nicht zum Absturz. Der Parser extrahiert, was möglich ist, und loggt Probleme.

```python
try:
    text = parser.extract_text(file_path)
except ParsingError as e:
    logger.warning(f"Parsing-Fehler in {file_path}: {e}")
    text = parser.extract_partial_text(file_path)
```

### Vollständigkeitsprüfung
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

### Verwendete Libraries

**PyMuPDF (fitz)** für PDF-Verarbeitung
- Schnell und zuverlässig
- Vollständige Textextraktion
- Tabellen-Support
```bash
pip install PyMuPDF
```

**python-docx** für Word-Dokumente
- Native DOCX-Unterstützung
- Formularfeld-Erkennung
- Tabellenextraktion
```bash
pip install python-docx
```

**openpyxl** für Excel-Files
- Vollständige Format-Unterstützung
- Multi-Sheet-Handling
- Formeln und Werte
```bash
pip install openpyxl
```

**langchain** als Orchestrierung für das RAG-System
- Text-Splitting
- Embedding-Integration
- Vector-Store-Anbindung
```bash
pip install langchain
```

**ChromaDB** als lokale Vektor-Datenbank
- Embedding-Speicherung
- Similarity-Search
- Metadaten-Filterung
```bash
pip install chromadb
```

### Code-Dokumentation

Der Code wird mit ausführlichen **Docstrings** dokumentiert. Jede Funktion erklärt ihre Parameter und Rückgabewerte. Beispiele zeigen die Verwendung.

**Beispiel:**
```python
def parse_document(file_path: Path) -> ParseResult:
    """
    Parst ein Dokument und extrahiert alle Informationen.
    
    Args:
        file_path: Pfad zur Datei (PDF, DOCX oder XLSX)
    
    Returns:
        ParseResult: Objekt mit volltext, struktur und metadaten
    
    Raises:
        ParsingError: Bei nicht unterstützten Formaten oder Parsing-Fehlern
    
    Example:
        >>> result = parse_document(Path("projektskizze.pdf"))
        >>> print(result.volltext[:100])
        "Projektname: Entwicklung einer..."
    """
    pass
```

---

## ⚡ PERFORMANCE-OPTIMIERUNG

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

Nach dem Parsing haben wir:

✅ **Vollständigen, durchsuchbaren Text** aller Dokumente  
✅ **Strukturierte Metadaten** für präzise Filterung  
✅ **Optimale Chunks** für RAG-Retrieval  
✅ **Erweiterbare Codebasis** für zukünftige Anforderungen  

### Beispiel-Output

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

## 🎓 ANWENDUNGSBEISPIEL

Das System ermöglicht es, Fragen wie:

**"Welche Voraussetzungen hat das PROFI-Programm?"**  
→ RAG findet relevante Textstellen aus Förderrichtlinien

**"Was steht in der Projektskizze zum Thema Innovation?"**  
→ RAG extrahiert Abschnitt "Technologischer Lösungsansatz"

**"Ist das Unternehmen KMU-berechtigt?"**  
→ RAG findet Informationen aus KMU-Erklärung und Jahresabschlüssen

präzise zu beantworten, indem es die relevanten Textstellen aus den geparsten Dokumenten findet und dem LLM zur Verfügung stellt.

---

## 🔐 SICHERHEIT

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