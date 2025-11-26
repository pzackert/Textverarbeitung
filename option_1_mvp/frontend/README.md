# IFB PROFI – Streamlit Frontend Skeleton

Minimaler Streamlit-Einstieg mit Logging, Button-Demo und eigenem Start-/Stop-Skript.

## Struktur

```
frontend/
├── Home.py          # Streamlit HOME-Seite mit Logging
├── start.py         # Startet Streamlit mit Live-Logs
├── stop.py          # Beendet laufende Streamlit-Prozesse
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

## Starten & Stoppen

```bash
# Streamlit mit Live-Logs starten (Browser öffnet automatisch)
cd frontend
python start.py

# Für weitere Kommandos einfach ein zweites Terminal öffnen

# Streamlit sauber beenden
python stop.py
```

- `start.py` streamt alle Logs direkt ins aktuelle Terminal (blocking).
- `stop.py` beendet alle Prozesse, die mit `streamlit run` laufen.
- App ist unter `http://localhost:8501` erreichbar.

## Hinweise
- `Home.py` nutzt ausschließlich Standard-Streamlit-Komponenten.
- Logging erfolgt über das Python-Logging-Modul (`INFO`-Level).
- Änderungen an Port/Optionen im `cmd`-Array in `start.py` anpassen.
