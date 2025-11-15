# IFB PROFI - Automatisierte Antragsprüfung# IFB PROFI - KI-gestützte Textverarbeitung

**Option 1 (Super-Lite MVP)** - LM Studio + Minimales RAG + Streamlit

## 📋 Projektübersicht

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

[![uv](https://img.shields.io/badge/package%20manager-uv-green)](https://github.com/astral-sh/uv)Automatisierte Antragsprüfung für IFB PROFI Förderanträge mit lokalem LLM (LM Studio + Qwen 2.5).



---**Version:** 1.0  

**Stand:** 31. Oktober 2025

## 📋 Was macht dieses System?

---

Automatische Prüfung von Förderanträgen gegen **6 IFB PROFI Kriterien**:

1. ✅ Antragssteller (KMU in Hessen?)## 🚀 Features

2. ✅ Förderkonformität (Innovationsprojekt?)

3. ✅ Fördersumme (10.000€ - 200.000€?)- ✅ **Wizard-basierte UI** (Streamlit) für 7-Schritte-Workflow

4. ✅ Projektlaufzeit (max. 2 Jahre?)- ✅ **Lokales LLM** (LM Studio + Qwen 2.5) - Kein Cloud-Upload

5. ✅ Projektkosten (plausibel?)- ✅ **RAG-System** (LangChain + ChromaDB) für intelligente Dokumentenanalyse

6. ✅ Rechtsform (GmbH, UG, etc.?)- ✅ **Multi-Format-Parser** (PDF, DOCX, XLSX)

- ✅ **Regelwerk-Engine** für Fördervoraussetzungen

**Features:**- ✅ **Automatische Checklisten & Reports**

- 📄 Dokumenten-Upload (PDF, DOCX, XLSX)

- 🤖 KI-gestützte Prüfung via lokalem LLM---

- 🔍 RAG (Retrieval Augmented Generation)

- 🎯 Strukturierte Ergebnis-Anzeige## 📁 Projektstruktur

- 🔒 100% lokal - keine Cloud

```

---masterprojekt/

├── backend/                    # Backend-Logik

## 🚀 Quickstart (3 Befehle)│   ├── parsers/               # PDF, DOCX, XLSX Parser

│   ├── rag/                   # RAG-System mit LangChain

```bash│   ├── regelwerk/             # Förderrichtlinien-Engine

# 1. Dependencies installieren│   ├── llm/                   # LM Studio Integration

uv sync│   └── utils/                 # Hilfsfunktionen

├── frontend/                   # Streamlit Frontend

# 2. LM Studio starten (läuft auf http://192.168.1.132:1234)│   ├── pages/                 # Wizard-Schritte (1-7)

│   └── components/            # UI-Komponenten

# 3. Streamlit App starten├── data/                       # Datenspeicherung

uv run streamlit run frontend/app.py│   ├── chromadb/              # Vector Store

```│   ├── projects/              # Projektdaten

│   ├── regelwerke/            # Förderrichtlinien

➡️ Browser öffnet sich automatisch auf `http://localhost:8501`│   └── input/                 # Input-Dateien zum Verarbeiten

├── tests/                      # Unit & Integration Tests

---├── config/                     # Konfigurationsdateien

├── docs/                       # Zusätzliche Dokumentation

## 🛠️ Installation│   ├── 01_Technische_Architektur.md

│   └── 02_Wizard_Flow.md

### Voraussetzungen└── requirements.txt            # Python Dependencies

- **Python 3.11+**```

- **UV Package Manager**: `pip install uv`

- **LM Studio** (läuft bereits auf 192.168.1.132:1234)---



### Setup## 🛠️ Tech-Stack

```bash

# Repo klonen| Komponente | Technologie | Version |

git clone <repo-url>|------------|-------------|---------|

cd masterprojekt| **Runtime** | Python | 3.11+ |

| **LLM-Server** | LM Studio | Latest |

# Dependencies installieren| **LLM-Modell** | Qwen 2.5 | 3B-7B |

uv sync| **RAG-Framework** | LangChain | 0.1+ |

| **Vector DB** | ChromaDB | 0.4.18+ |

# App starten| **Frontend** | Streamlit | 1.28+ |

uv run streamlit run frontend/app.py| **Embeddings** | sentence-transformers | 2.2+ |

```

---

---

## 📦 Installation

## 📖 Benutzung

### 1. Python-Umgebung einrichten

1. **Upload**: Dokumente hochladen (PDF/DOCX/XLSX)

2. **Prüfung**: Kriterien automatisch prüfen lassen```bash

3. **Ergebnisse**: ✅ Erfüllt / ⚠️ Unsicher / ❌ Nicht erfüllt# Virtual Environment erstellen

python -m venv venv

---

# Aktivieren

## 🗂️ Projekt-Struktursource venv/bin/activate  # macOS/Linux

# oder

```venv\Scripts\activate     # Windows

masterprojekt/

├── frontend/          # Streamlit UI# Dependencies installieren

├── backend/           # Parser, RAG, LLM, Criteriapip install -r requirements.txt

├── config/            # config.yaml```

├── data/              # Uploads, ChromaDB, Results

├── pyproject.toml     # UV Dependencies### 2. LM Studio installieren

├── TASKS.md           # Implementierungs-Plan

└── README.md          # Diese Datei1. Download: https://lmstudio.ai/

```2. Modell herunterladen: **Qwen 2.5 3B** oder **7B**

3. Server starten (Port 1234)

---

```bash

## 📚 Dokumentation# Optional: CLI-Server

lms server start --model qwen2.5-3b-instruct

Siehe `docs/` für Details:```

- **PROJECT_OVERVIEW.md** - Gesamtübersicht

- **VALIDATION_REPORT.md** - Machbarkeits-Analyse### 3. Projekt konfigurieren

- **TASKS.md** - Schritt-für-Schritt Implementierung

```bash

---# Config-Datei erstellen

cp config/config.example.yaml config/config.yaml

**Status:** 🚧 In aktiver Entwicklung (Option 1 MVP)

# Anpassen nach Bedarf (LM Studio URL, Ports, etc.)
```

---

## 🚀 Verwendung

### Frontend starten

```bash
streamlit run frontend/app.py
```

### 7-Schritte-Workflow

1. **Projekt anlegen** - Metadaten erfassen
2. **Dokumente hochladen** - PDF, DOCX, XLSX
3. **Dokumente parsen** - Text & Daten extrahieren
4. **Informationsextraktion** - RAG-basierte Analyse
5. **Fördervoraussetzungen prüfen** - Regelwerk anwenden
6. **Bewertung durchführen** - Scoring & Plausibilität
7. **Report & Checkliste generieren** - Markdown/PDF Export

---

## 📂 Input-Ordner

Der Ordner `data/input/` ist für Dateien vorgesehen, die verarbeitet werden sollen:

```bash
data/input/
├── projektskizze.pdf
├── kalkulation.xlsx
└── ...
```

Nach Verarbeitung werden die Ergebnisse in `data/projects/projekt_XXX/` gespeichert.

---

## 🧪 Tests

```bash
# Unit Tests
pytest tests/unit/

# Integration Tests
pytest tests/integration/

# Alle Tests
pytest
```

---

## 📖 Dokumentation

Siehe `docs/` für detaillierte Dokumentation:

- **01_Technische_Architektur.md** - System-Design & Tech-Stack
- **02_Wizard_Flow.md** - Schritt-für-Schritt UI-Logik

---

## 🔒 Datenschutz

- ✅ **100% lokal** - Keine Cloud-Anbindung
- ✅ **Kein Daten-Upload** - Alles läuft auf lokaler Hardware
- ✅ **DSGVO-konform** - Sensible Antragsdaten bleiben privat

---

## 📝 Lizenz

Internes Projekt - Alle Rechte vorbehalten.

---

## 👨‍💻 Entwicklung

### Nächste Schritte

- [ ] Parser für PDF, DOCX, XLSX implementieren
- [ ] RAG-Pipeline mit LangChain aufbauen
- [ ] LM Studio Integration testen
- [ ] Streamlit UI entwickeln (7 Seiten)
- [ ] Regelwerk-Engine implementieren
- [ ] Tests schreiben

### Version History

- **1.0** (31.10.2025) - Initiale Projektstruktur
