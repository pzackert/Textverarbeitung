# Frontend Status - IFB PROFI

## Projekt-Überblick
IFB PROFI ist eine lokale AI-Plattform zur Prüfung von Förderanträgen. Das System analysiert Dokumente (PDF, DOCX, XLSX) mittels RAG (Retrieval Augmented Generation) und bewertet sie anhand definierter Kriterien (in `config.yaml`). Der Fokus liegt auf Datenschutz (lokale Ausführung mit Ollama/ChromaDB).

## Tech Stack
**Frontend:**
- **Framework**: FastAPI (Server-Side Rendering)
- **Templating**: Jinja2 Templates
- **Interaktivität**: HTMX (für dynamische Updates ohne Full Page Reload)
- **Styling**: TailwindCSS (aktuell via CDN)
- **Server**: Uvicorn

**Backend (integriert):**
- **Framework**: FastAPI (Core Services in `src/`)
- **Datenbank**: ChromaDB (Vektor-Store für RAG)
- **LLM**: Ollama (Client via `httpx`)
- **Parsing**: Docling, PyMuPDF (via `src/parsers`)

## Frontend-Struktur
Das Frontend ist als Python-Modul `frontend` organisiert, das direkt auf die `src`-Services zugreift:

```
frontend/
├── main.py                 # Entry Point (FastAPI App)
├── routers/                # Seiten-Logik (Dashboard, Projects, Chat)
├── templates/              # Jinja2 HTML Templates
├── static/                 # Assets (CSS/JS/Images)
└── services/               # Frontend-spezifische Helper (z.B. api_client.py)
```

## Startup-Prozess
**Aktuell (Monolith):**
Das Frontend und Backend laufen im selben Prozess.

```bash
# Startbefehl (aus package.json oder Dev)
uv run python -m frontend.main
# Oder via Uvicorn direkt:
uv run uvicorn frontend.main:app --reload --port 8000
```

## Dependencies
Verwaltung erfolgt über `pyproject.toml` (UV).
**Wichtige Frontend-Packages:**
- `fastapi`, `uvicorn`: Webserver
- `jinja2`: Template Engine
- `pydantic`: Datenvalidierung
- `httpx`: Async HTTP Client (für Ollama-Calls)

**Wichtige Backend-Packages (via `src`):**
- `chromadb`, `sentence-transformers`: RAG
- `docling`, `pymupdf`: Dokumenten-Parsing

## Backend-Integration
**Typ**: **Direkter Import (Monolith)**
Das Frontend (`frontend/routers/`) importiert die Backend-Services direkt aus `src/services/`.

Beispiel (`frontend/routers/projects.py`):
```python
from src.services.project_service import project_service
from src.services.chat_service import chat_service
```

**Verwendung:**
- Das Frontend ruft direkt Python-Methoden auf (`project_service.get_project(...)`).
- Es gibt **keine** interne REST-API zwischen Frontend und Backend-Logik (außer der API, die das Frontend selbst bereitstellt).

## Aktueller Zustand
**Funktioniert:** Ja, die App startet und zeigt UI an (basierend auf README/Code).
**Probleme erkannt:**
- **Mock-Logik in Routern:** Teile der Logik (z.B. Chat-Antworten in `projects.py`) sind noch hardcoded/gemockt, obwohl Services importiert werden.
- **CDN Nutzung:** TailwindCSS wird via CDN geladen, was offline (lokal) problematisch sein könnte.
- **Daten-Persistenz:** README erwähnt, dass Änderungen z.T. nur im Speicher gehalten werden (muss verifiziert werden, `project_service` scheint aber zu existieren).

**Nächste Schritte:**
- **Integration finalisieren:** Mock-Logik in `routers/` durch echte Service-Calls ersetzen (Phase 7).
- **Offline-Fähigkeit:** TailwindCSS lokal einbinden (Build-Step).
