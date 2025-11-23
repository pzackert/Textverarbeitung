# IFB PROFI - Installation & Start

## Schnellstart

### Option 1: Mit UV (empfohlen) ⭐

```bash
# 1. Dependencies installieren
uv sync

# 2. Streamlit starten
cd frontend
python start.py
```

### Option 2: Mit venv (alternativ)

```bash
# 1. Virtual Environment aktivieren
source venv/bin/activate
pip install -e .

# 2. Streamlit starten
cd frontend
python start.py
```

Oder nutze das Start-Script:
```bash
./start.sh
```

## System-Architektur

**Option 1: Super-Lite MVP** ✅ IMPLEMENTIERT

- **LLM**: LM Studio + Qwen 4B (http://192.168.1.132:1234)
- **RAG**: ChromaDB + sentence-transformers
- **Parser**: PyMuPDF, python-docx, openpyxl
- **UI**: Streamlit
- **Storage**: Lokales Filesystem (JSON)

## Komponenten-Status

### ✅ Phase 1: Setup & Infrastructure (FERTIG)
- Python 3.13.7
- Alle Dependencies installiert
- Projekt-Struktur erstellt
- Config-System (YAML)
- Logging-System
- LM Studio Connection getestet

### ✅ Phase 2: Document Parsing (FERTIG)
- PDF Parser (PyMuPDF)
- DOCX Parser (python-docx)
- XLSX Parser (openpyxl)
- Parser Manager mit Validierung
- File-Upload Unterstützung

### ✅ Phase 3: RAG System (FERTIG)
- Text Chunker (character-based, mit Overlap)
- ChromaDB VectorStore
- Sentence-Transformers Embeddings (multilingual-MiniLM)
- Similarity Search
- Document Management

### ✅ Phase 4: LLM Integration (FERTIG)
- LM Studio Client (OpenAI-kompatibel)
- Einfache Prompt-Templates
- RAG-Context Integration
- Error Handling

### ✅ Phase 5: Criteria Engine (FERTIG)
- 6 Hauptkriterien implementiert:
  - Antragssteller (Berechtigung, Sitz)
  - Förderkonformität (Förderfähige Maßnahmen)
  - Fördersumme (Grenzwerte)
  - Projektlaufzeit (Angemessenheit)
  - Projektkosten (Nachvollziehbarkeit)
  - Rechtsform (Förderfähigkeit)
- LLM-gestützte Bewertung
- Strukturierte Ergebnisse

### ✅ Phase 6: Streamlit UI (FERTIG)
- Home-Page mit Übersicht
- Dokument-Upload (Multi-File)
- Kriterien-Prüfung
- Ergebnis-Darstellung
- Navigation & Session Management

### ✅ Phase 7: Integration & Testing (FERTIG)
- Integrations-Test (tests/integration/test_workflow.py)
- Component-Tests
- End-to-End Workflow
- Dokumentation

## Verwendung

### 1. Regelwerk indexieren

Zuerst müssen die IFB-Förderrichtlinien indexiert werden:

```python
from backend.rag.vector_store import VectorStore
from backend.parsers.parser_manager import DocumentParser
from backend.rag.chunker import chunk_text
from pathlib import Path

# Parser & VectorStore
parser = DocumentParser()
store = VectorStore()

# Regelwerk-Dokumente parsen
regelwerk_dir = Path("data/regelwerke")
for doc_path in regelwerk_dir.glob("*.pdf"):
    result = parser.parse(doc_path)
    
    # Chunken
    chunks = chunk_text(result['text'])
    
    # Indexieren
    metadatas = [{"doc_id": doc_path.stem, "chunk_id": i} 
                 for i in range(len(chunks))]
    ids = [f"{doc_path.stem}_{i}" for i in range(len(chunks))]
    
    store.add_documents(chunks, metadatas, ids)
```

### 2. Antrag prüfen

```python
from backend.core.criteria_engine import CriteriaEngine
from backend.parsers.parser_manager import DocumentParser

# Antrag parsen
parser = DocumentParser()
antrag = parser.parse(Path("data/input/antrag.pdf"))

# Kriterien prüfen
engine = CriteriaEngine()
results = engine.check_all_criteria(antrag['text'])

print(f"Gesamt-Status: {results['overall_status']}")
print(f"Zusammenfassung: {results['summary']}")

for result in results['criteria_results']:
    print(f"\n{result['criterion']}: {result['status']}")
    print(f"  {result['reasoning']}")
```

### 3. Streamlit UI nutzen

```bash
# UI starten
cd frontend
python start.py
```

Dann im Browser:
1. Dokumente hochladen (Projektskizze, Kostenplan, etc.)
2. Kriterien-Prüfung starten
3. Ergebnisse ansehen

## Konfiguration

Alle Einstellungen in `config/config.yaml`:

```yaml
llm:
  base_url: "http://192.168.1.132:1234/v1"
  model: "qwen2.5-4b-instruct"
  temperature: 0.1

rag:
  chunk_size: 500
  chunk_overlap: 50
  top_k: 3
  embedding_model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
```

## Troubleshooting

### ChromaDB Fehler beim Start
```
Failed to send telemetry event: capture() takes 1 positional argument but 3 were given
```

**Behebung:**
```bash
# ChromaDB zurücksetzen
rm -rf data/chromadb

# App neu starten - wird automatisch neu initialisiert
python frontend/start.py
```

⚠️ **Hinweis:** Dieser Fehler tritt beim ersten Start auf, ist aber nicht kritisch. Nach der Reinitialisierung funktioniert alles einwandfrei.

### LM Studio nicht erreichbar
```bash
# Teste Verbindung
python tests/test_lm_studio.py
```

Stelle sicher:
- LM Studio läuft auf http://192.168.1.132:1234
- Ein Modell ist geladen (Qwen 2.5 4B empfohlen)

### ChromaDB Fehler (Datenbankfehler)
```bash
# Lösche ChromaDB und neu initialisieren
rm -rf data/chromadb
python -c "from backend.rag.vector_store import VectorStore; VectorStore()"
```

### SentenceTransformers Fehler
Falls HuggingFace-Fehler auftreten:
```bash
uv pip install --upgrade sentence-transformers huggingface-hub
```

### Import-Fehler
```bash
# Stelle sicher PYTHONPATH ist gesetzt
export PYTHONPATH=/Users/patrick.zackert/projects/masterprojekt
```

## Nächste Schritte (Option 2+)

Folgende Features sind für spätere Versionen geplant:

- **OOP-Architektur** für Parser (OPTION 2+)
- **Parallele Verarbeitung** (OPTION 2+)
- **FastAPI Backend** (OPTION 2+)
- **Redis Caching** (OPTION 2+)
- **OCR für gescannte PDFs** (OPTION 2+)
- **Erweiterte Struktur-Extraktion** (OPTION 2+)
- **Multi-User Support** (OPTION 2+)
- **Datenbank-Integration** (OPTION 2+)

## Lizenz

Internes Projekt - IFB Thüringen
