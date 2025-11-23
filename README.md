# IFB PROFI - KI-gestützte Antragsprüfung

**Automatisierte Validierung von Förderanträgen** mit lokalem KI-System und Kriterienkatalog.

## 🎯 Projektübersicht

Diese Anwendung ermöglicht die **strukturierte Prüfung von Förderanträgen** durch:
- Automatische Datenextraktion aus verschiedenen Dokumentformaten
- Validierung anhand eines definierten Kriterienkatalogs
- KI-gestützte Plausibilitätsprüfung und Bewertung
- Übersichtliche Darstellung der Prüfergebnisse

### Workflow
**Geführter Wizard-Flow (Streamlit):**
1. Projekt im Dashboard anlegen (Hero + Sidebar-Suche)
2. Dokumentkarten mit Kriterien-Beschreibung aus `config/criteria_catalog.json` befüllen
3. Automatische Prüfung (Parsing → RAG → Kriterienengine) inkl. Fortschrittsbalken
4. Ergebnisse tabellarisch auswerten & JSON exportieren

## ✨ Features

- 📊 **Projekt-Management:** Übersicht aller Prüfprojekte inkl. Sidebar-Suche & Status-Badges
- 🎛 **Wizard mit Fortschrittsbalken:** Permanent sichtbare Steps (Metadaten → Upload → Prüfung → Ergebnisse)
- 📄 **Dokumentkarten mit Kontext:** Jede Upload-Kachel zeigt Beschreibung & Kriterien aus dem Katalog
- 🤖 **Lokales LLM:** LM Studio oder andere OpenAI-kompatible Server (private Cloud möglich)
- 🔍 **RAG-System:** ChromaDB + sentence-transformers für kontextbasierte Analyse
- ⚙️ **Regelwerk-Engine:** Automatische Prüfung gegen Fördervoraussetzungen
- ✅ **Demo-Projekt:** Seeder legt ein vorführbares Referenzprojekt automatisch an
- 🔒 **Datenschutz:** 100% lokal, keine externen Cloud-Dienste

## 📁 Projektstruktur

```
masterprojekt/
├── backend/          # Core-Logik
│   ├── parsers/      # PDF, DOCX, XLSX Parser
│   ├── rag/          # ChromaDB, Chunking, Embeddings
│   ├── llm/          # LM Studio Client
│   ├── core/         # Criteria Engine
│   └── utils/        # Config, Logger
├── frontend/         # Streamlit UI
│   ├── app.py        # Wizard (Sidebar + Progress)
│   ├── components/   # Sidebar, Progress Tracker & Cards
│   ├── services/     # Project-/Process-Services (Backend Calls)
│   ├── styles/       # IFB Copalette CSS
│   └── pages/        # Legacy Seiten (optional)
├── config/           # YAML-Konfiguration
├── data/             # Projekte, ChromaDB, Input
├── docs/             # Detaillierte Dokumentation
└── tests/            # Unit & Integration Tests
```

## 🛠 Tech-Stack

### Backend
- **Python:** 3.11+
- **Parser:** PyMuPDF, python-docx, openpyxl
- **RAG:** ChromaDB, sentence-transformers
- **LLM:** OpenAI-kompatible API (LM Studio, Ollama, etc.)

### Frontend
- **Streamlit:** Webbasierte UI

### LLM-Server
Verschiedene Optionen möglich (in Evaluation):
- LM Studio (lokal)
- Ollama (lokal)
- Private Cloud-Deployment
- Modell: Qwen, Llama, Mistral (je nach Anforderung)

## 🚀 Installation & Setup

### Voraussetzungen
- Python 3.11+
- UV Package Manager oder venv
- LM Studio oder alternativer LLM-Server

### Installation

**Mit UV (empfohlen):**
```bash
# 1. Repository klonen
git clone <repo-url>
cd masterprojekt

# 2. Dependencies installieren
uv sync

# 3. Config anpassen
cp config/config.example.yaml config/config.yaml
# LLM-Server URL in config.yaml eintragen

# 4. Anwendung starten
python frontend/start.py
```

**Mit venv (alternativ):**
```bash
# 1. Repository klonen
git clone <repo-url>
cd masterprojekt

# 2. Virtual Environment erstellen
python3 -m venv venv
source venv/bin/activate

# 3. Dependencies installieren
pip install -e .

# 4. Config anpassen
cp config/config.example.yaml config/config.yaml

# 5. Anwendung starten
python frontend/start.py
```

### Anwendung starten

```bash
# Streamlit UI mit Live-Logs starten
cd frontend
python start.py

# In zweitem Terminal weiterarbeiten oder Copilot verwenden

# Zum Beenden (neues Terminal)
python stop.py
```

- Die Start-Routine nutzt das virtuelle Environment unter `venv/` und öffnet den Browser automatisch.
- Live-Logs erscheinen direkt im Terminal; zum Beenden `Strg+C` oder `python stop.py` verwenden.
- App läuft auf: **http://localhost:8501**

## 📚 Dokumentation

Detaillierte Dokumentationen im `docs/` Ordner:
- **01-08:** Komponenten-spezifische Dokumentation (UI, Parsing, RAG, LLM, etc.)
- **GETTING_STARTED.md:** Schnellstart-Anleitung
- **PROJECT_OVERVIEW.md:** Architektur-Übersicht
- **TECHNICAL_REQUIREMENTS.md:** System & Tech-Anforderungen

## 🔐 Datenschutz & Sicherheit

- **Lokal-First:** Alle Daten bleiben auf lokalem System oder privater Cloud
- **Keine externen APIs:** LLM läuft komplett lokal
- **Dateibasiert:** Projekte in `data/projects/`, keine externe Datenbank
- **Single-User:** MVP für Einzelnutzung (Multi-User in zukünftigen Versionen)

## 🧪 Tests

```bash
# Unit Tests
uv run pytest tests/unit/

# Integration Tests
uv run pytest tests/integration/
```

## 📝 Lizenz

[Lizenz hier einfügen]

---

**Version:** 1.0 (Option 1 MVP)  
**Stand:** November 2025
