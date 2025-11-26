# Option 2: Professional AI Platform

Dies ist die Weiterentwicklung des MVP zu einer robusten, modularen Plattform.

## Architektur
Die Anwendung folgt einer Service-orientierten Architektur mit FastAPI im Backend und einer HTMX-basierten Frontend-Integration.

### Tech Stack
- **Backend:** FastAPI, Pydantic, Dependency Injection.
- **Frontend:** Jinja2 Templates, HTMX, TailwindCSS.
- **LLM:** Ollama (Lokal), LangChain (Utilities).
- **Datenbank:** ChromaDB (Vektor), SQLite/Postgres (Metadaten - geplant).

## Setup

### Voraussetzungen
- Python 3.12+
- `uv` Package Manager
- Ollama (installiert und laufend)

### Installation
```bash
cd option_2_platform
uv venv
source .venv/bin/activate
uv pip install -r frontend/requirements.txt # Temporär, wird konsolidiert
```

### Starten
```bash
./start_v2.sh
```
