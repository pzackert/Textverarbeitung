# IFB PROFI – Streamlit Frontend Skeleton

Minimaler Streamlit-Einstieg mit Logging, Button-Demo und eigenem Startskript.

## Struktur

```
frontend/
├── Home.py          # Streamlit HOME-Seite mit Logging
├── start.py         # Startet Streamlit im Hintergrund
├── requirements.txt # Benötigte Python-Dependencies
└── README.md        # Diese Anleitung
```

## Setup

```bash
# Aus dem Projekt-Root
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r frontend/requirements.txt
```

## Starten

```bash
# Start in background (default) and free the terminal
python frontend/start.py

# Attach to logs in the current terminal (blocking)
python frontend/start.py --attach
```

- Logs in background mode land in `frontend/streamlit.log`. Follow them with:

```bash
tail -f frontend/streamlit.log
```

- Das Skript öffnet Streamlit auf `http://localhost:8501` und hält das Terminal frei.
- Logs zu Button-Klicks erscheinen direkt im Terminal.
- Stoppen über `pkill -f "streamlit run"` oder den ausgegebenen PID.

## Hinweise
- `Home.py` nutzt ausschließlich Standard-Streamlit-Komponenten.
- Logging erfolgt über das Python-Logging-Modul (`INFO`-Level).
- Änderungen an Port/Optionen im `command` von `start.py` anpassen.
