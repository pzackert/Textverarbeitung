# IFB PROFI Frontend

The frontend for the IFB Document Analysis Platform.

## Architecture

- **Framework:** FastAPI (Server-Side Rendering)
- **Templating:** Jinja2
- **Interactivity:** HTMX
- **Styling:** Tailwind CSS
- **State:** Alpine.js

## Integration

The frontend communicates with the RAG Backend via the API Layer (`src/api`).
All API calls are handled by `frontend/services/api_client.py`.

## Features

- **Dashboard:** Overview of projects and system status.
- **Projects:** Manage document uploads.
- **Chat:** Interactive Q&A with the RAG system.

## Development

Start the full application (Frontend + API):
```bash
python scripts/start_app.py
```

## Directory Structure

- `routers/`: FastAPI route handlers.
- `services/`: Business logic and API client.
- `templates/`: HTML templates.
- `static/`: CSS/JS assets.

Voraussetzung: [uv](https://github.com/astral-sh/uv) ist installiert.

1. Repository klonen (falls nicht geschehen).
2. In das Projektverzeichnis wechseln.
3. Abhängigkeiten installieren:

```bash
uv sync
```

## Starten der Anwendung

```bash
uv run uvicorn frontend_v2.main:app --reload
```

Die Anwendung ist dann unter `http://localhost:8000` erreichbar.

## Tests ausführen

```bash
uv run pytest tests/test_frontend_v2.py
```

## Projektstruktur

```
frontend_v2/
├── main.py                 # Entry Point
├── mock_data.py            # Mock Daten Generator
├── routers/                # API Routen
│   ├── dashboard.py
│   ├── projects.py
│   ├── criteria.py
│   └── wizard.py
├── static/                 # Statische Assets (CSS, JS, Images)
└── templates/              # Jinja2 Templates
    ├── base.html           # Basis Layout
    ├── index.html          # Dashboard
    ├── projects_list.html  # Antragsliste
    ├── project_detail.html # Einzelansicht
    └── wizard/             # Wizard Steps
```

## Mock User

Das System verwendet aktuell Mock-Daten. Es ist kein Login erforderlich.
Die Rollen werden simuliert.

## Bekannte Limitierungen

- **Datenpersistenz**: Aktuell werden Änderungen nur im Speicher gehalten (Mock-Daten). Ein Neustart setzt die Daten zurück.
- **Dokumenten-Scan**: Der Scan ist simuliert (Mock).
- **Tailwind**: Verwendet CDN Script. Für Produktion sollte ein Build-Step eingerichtet werden.
Das System simuliert den eingeloggten Benutzer "Max Mustermann".

## Bekannte Limitierungen

- **Datenpersistenz**: Änderungen werden aktuell nicht dauerhaft gespeichert (In-Memory Mock Data).
- **Tailwind CSS**: Nutzt CDN für schnelle Entwicklung. Für Produktion sollte ein Build-Prozess eingerichtet werden.
- **Authentifizierung**: Nur UI-Mockup, keine echte Sicherheitsprüfung.
