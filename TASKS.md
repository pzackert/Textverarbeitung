# OPTION 1 IMPLEMENTATION TASKS
**Ziel:** Funktionierender MVP mit LM Studio + minimales RAG + Streamlit

---

## ✅ PHASE 0: SETUP & CLEANUP
- [x] Tasks-Ordner gelöscht
- [x] GETTING_STARTED.md nach docs/ verschoben
- [x] README.md erstellt (Root-Level)
- [x] Requirements bereinigt (nur Option 1)
- [x] UV-Setup implementiert (pyproject.toml)
- [x] `uv sync` läuft ohne Fehler ✅
- **Status:** ABGESCHLOSSEN

---

## 🔧 PHASE 1: MINIMAL ENVIRONMENT

### Task 1.1: UV-Projekt initialisieren
- [ ] `uv init` ausführen
- [ ] `pyproject.toml` erstellen mit Projekt-Metadaten
- [ ] Python 3.11+ als Minimum festlegen
- **Test:** `uv sync` funktioniert

### Task 1.2: Core Dependencies installieren
```toml
dependencies = [
    "streamlit>=1.28.0",
    "pymupdf>=1.23.0",
    "python-docx>=1.0.0",
    "openpyxl>=3.1.0",
    "chromadb>=0.4.15",
    "sentence-transformers>=2.2.0",
    "openai>=1.3.0",  # für LM Studio API
    "pyyaml>=6.0.0",
]
```
- **Test:** `uv run python -c "import streamlit; print('OK')"` funktioniert

### Task 1.3: Config-Datei erstellen
- [ ] `config/config.yaml` mit LM Studio URL: `http://192.168.1.132:1234`
- [ ] Minimale Einstellungen (chunk_size, top_k, etc.)
- **Test:** Config laden funktioniert

### Task 1.4: Logger einrichten
- [ ] `backend/utils/logger.py` - einfaches Python logging
- [ ] Ausgabe in Console + File (`logs/app.log`)
- **Test:** `logger.info("Test")` funktioniert

---

## 📄 PHASE 2: DOCUMENT PARSING

### Task 2.1: PDF Parser (PyMuPDF)
- [ ] `backend/parsers/pdf_parser.py`
- [ ] Funktion: `parse_pdf(path: Path) -> str` (nur Text!)
- [ ] Keine Struktur-Erkennung, nur `.get_text()`
- **Test:** PDF aus `data/input/` parsen und Text ausgeben

### Task 2.2: DOCX Parser (python-docx)
- [ ] `backend/parsers/docx_parser.py`
- [ ] Funktion: `parse_docx(path: Path) -> str`
- [ ] Nur Paragraphen-Text extrahieren
- **Test:** DOCX parsen und Text ausgeben

### Task 2.3: XLSX Parser (openpyxl)
- [ ] `backend/parsers/xlsx_parser.py`
- [ ] Funktion: `parse_xlsx(path: Path) -> str`
- [ ] Zellen als Text mit Pipe-Separator
- **Test:** XLSX parsen und Text ausgeben

### Task 2.4: Parser Router
- [ ] `backend/parsers/parser.py`
- [ ] Funktion: `parse_document(path: Path) -> str`
- [ ] Automatische Erkennung via Extension
- **Test:** Alle 3 Formate durchlaufen

---

## 🔍 PHASE 3: RAG SYSTEM

### Task 3.1: Text Chunker
- [ ] `backend/rag/chunker.py`
- [ ] Funktion: `chunk_text(text: str, size=500, overlap=50) -> List[str]`
- [ ] Einfaches Character-basiertes Chunking
- **Test:** 1000 Zeichen Text → mehrere Chunks mit Overlap

### Task 3.2: ChromaDB Setup
- [ ] `backend/rag/vector_store.py`
- [ ] Initialisiere ChromaDB Collection
- [ ] Persistenz in `data/chromadb/`
- **Test:** Collection erstellen und schließen

### Task 3.3: Embedding-Funktion
- [ ] `backend/rag/embedder.py`
- [ ] Lade `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`
- [ ] Funktion: `embed_text(text: str) -> List[float]`
- **Test:** "Hallo Welt" → Embedding-Vektor

### Task 3.4: Dokument indexieren
- [ ] Funktion: `index_document(doc_id: str, chunks: List[str])`
- [ ] Chunks embedden + in ChromaDB speichern
- **Test:** Test-Dokument indexieren, Collection-Count prüfen

### Task 3.5: Retrieval-Funktion
- [ ] Funktion: `retrieve(query: str, top_k=3) -> List[str]`
- [ ] Query embedden → ChromaDB Similarity Search
- **Test:** Query "Projektlaufzeit" → relevante Chunks zurück

---

## 🤖 PHASE 4: LLM INTEGRATION

### Task 4.1: LM Studio Connection Test
- [ ] `backend/llm/lm_studio.py`
- [ ] Test-Funktion: `test_connection() -> bool`
- [ ] Checke `/v1/models` Endpoint
- **Test:** Connection zu `http://192.168.1.132:1234` erfolgreich

### Task 4.2: LLM Client (OpenAI-kompatibel)
- [ ] `backend/llm/client.py`
- [ ] Funktion: `generate(prompt: str, system: str = None) -> str`
- [ ] Nutze `openai` Library für LM Studio
- **Test:** "Was ist 2+2?" → "4"

### Task 4.3: Prompt Templates
- [ ] `backend/llm/prompts.py`
- [ ] Template für Kriterien-Prüfung (System + User Prompt)
- [ ] Variablen: `{context}`, `{criterion}`, `{question}`
- **Test:** Template mit Dummy-Daten füllen

### Task 4.4: RAG + LLM kombinieren
- [ ] Funktion: `rag_query(question: str, doc_id: str) -> str`
- [ ] Retrieval → Kontext zusammenstellen → LLM befragen
- **Test:** Frage an indexiertes Dokument

---

## ⚖️ PHASE 5: CRITERIA ENGINE

### Task 5.1: Kriterien definieren
- [ ] `backend/core/criteria.py`
- [ ] Dict mit 6 Kriterien + Prüffragen
- [ ] Beispiel: `"antragssteller": "Ist der Antragssteller ein KMU in Hessen?"`
- **Test:** Alle 6 Kriterien ausgeben

### Task 5.2: Einzelne Kriterien-Prüfung
- [ ] Funktion: `check_criterion(doc_id: str, criterion: str) -> dict`
- [ ] RAG-Retrieval + LLM-Befragung
- [ ] Return: `{criterion, passed: bool, confidence, reasoning}`
- **Test:** Ein Kriterium an Test-Dokument prüfen

### Task 5.3: Vollständige Prüfung
- [ ] Funktion: `check_all_criteria(doc_id: str) -> List[dict]`
- [ ] Alle 6 Kriterien sequenziell durchlaufen
- [ ] Fortschritt loggen
- **Test:** Vollständige Prüfung eines Dokuments

---

## 🖥️ PHASE 6: STREAMLIT UI

### Task 6.1: Basis-App Setup
- [ ] `frontend/app.py` (Haupt-Einstieg)
- [ ] Streamlit Page Config (Titel, Icon, Layout)
- [ ] Sidebar mit Navigation (Upload, Prüfung, Ergebnisse)
- **Test:** `cd frontend && python start.py` läuft

### Task 6.2: Upload-Page
- [ ] `frontend/pages/1_upload.py`
- [ ] File Uploader (PDF/DOCX/XLSX)
- [ ] Dokument speichern in `data/input/{project_id}/`
- [ ] Parse-Button → Parsing + Indexierung
- **Test:** Datei hochladen, Text anzeigen

### Task 6.3: Prüfung-Page
- [ ] `frontend/pages/2_pruefung.py`
- [ ] Projekt-Auswahl (aus `data/input/`)
- [ ] "Prüfung starten"-Button
- [ ] Progress Bar + Live-Logging
- **Test:** Prüfung starten, Fortschritt sehen

### Task 6.4: Ergebnisse-Page
- [ ] `frontend/pages/3_ergebnisse.py`
- [ ] Ergebnisse aus JSON laden (`data/results/{project_id}.json`)
- [ ] Tabelle: Kriterium | Status | Begründung
- [ ] Ampel-System (✅ Erfüllt, ⚠️ Unsicher, ❌ Nicht erfüllt)
- **Test:** Ergebnisse anzeigen

---

## ✅ PHASE 7: INTEGRATION & TEST

### Task 7.1: End-to-End Test
- [ ] Test-Dokument vorbereiten (z.B. Beispiel-Antrag als PDF)
- [ ] Kompletter Workflow: Upload → Parse → Index → Prüfen → Ergebnisse
- **Test:** Alle Schritte ohne Fehler durchlaufen

### Task 7.2: Error Handling
- [ ] Try-Catch in allen kritischen Funktionen
- [ ] Aussagekräftige Error-Messages
- [ ] Graceful Degradation (z.B. wenn LM Studio offline)
- **Test:** LM Studio stoppen → saubere Fehlermeldung

### Task 7.3: README.md finalisieren
- [ ] Installation mit UV
- [ ] LM Studio Setup
- [ ] Quickstart (3 Commands)
- [ ] Screenshot/GIF
- **Test:** README durchgehen, funktioniert alles?

---

## 📋 VALIDIERUNG & NEXT STEPS

### Abnahme-Kriterien (ALLE müssen erfüllt sein):
- [ ] `uv sync` läuft ohne Fehler
- [ ] Streamlit startet: `cd frontend && python start.py`
- [ ] LM Studio Connection funktioniert
- [ ] PDF/DOCX/XLSX können geparst werden
- [ ] RAG Retrieval liefert relevante Chunks
- [ ] LLM antwortet auf Fragen
- [ ] Alle 6 Kriterien werden geprüft
- [ ] Ergebnisse werden angezeigt
- [ ] README ist verständlich

### Optional (nach MVP):
- [ ] Beispiel-Dokumente in `data/examples/`
- [ ] Docker-Container für LM Studio?
- [ ] CI/CD Pipeline?

---

**Arbeitsweise:**
1. **Ein Task nach dem anderen**
2. **Jeder Task wird getestet bevor weiter**
3. **Minimalistisch - keine Extras!**
4. **Logging statt Print**
5. **Temp-Files nach Test löschen**
