# IFB PROFI - KI-gestützte Textverarbeitung

## 📋 Projektübersicht

Automatisierte Antragsprüfung für IFB PROFI Förderanträge mit lokalem LLM (LM Studio + Qwen 2.5).

**Version:** 1.0  
**Stand:** 31. Oktober 2025

---

## 🚀 Features

- ✅ **Wizard-basierte UI** (Streamlit) für 7-Schritte-Workflow
- ✅ **Lokales LLM** (LM Studio + Qwen 2.5) - Kein Cloud-Upload
- ✅ **RAG-System** (LangChain + ChromaDB) für intelligente Dokumentenanalyse
- ✅ **Multi-Format-Parser** (PDF, DOCX, XLSX)
- ✅ **Regelwerk-Engine** für Fördervoraussetzungen
- ✅ **Automatische Checklisten & Reports**

---

## 📁 Projektstruktur

```
masterprojekt/
├── backend/                    # Backend-Logik
│   ├── parsers/               # PDF, DOCX, XLSX Parser
│   ├── rag/                   # RAG-System mit LangChain
│   ├── regelwerk/             # Förderrichtlinien-Engine
│   ├── llm/                   # LM Studio Integration
│   └── utils/                 # Hilfsfunktionen
├── frontend/                   # Streamlit Frontend
│   ├── pages/                 # Wizard-Schritte (1-7)
│   └── components/            # UI-Komponenten
├── data/                       # Datenspeicherung
│   ├── chromadb/              # Vector Store
│   ├── projects/              # Projektdaten
│   ├── regelwerke/            # Förderrichtlinien
│   └── input/                 # Input-Dateien zum Verarbeiten
├── tests/                      # Unit & Integration Tests
├── config/                     # Konfigurationsdateien
├── docs/                       # Zusätzliche Dokumentation
│   ├── 01_Technische_Architektur.md
│   └── 02_Wizard_Flow.md
└── requirements.txt            # Python Dependencies
```

---

## 🛠️ Tech-Stack

| Komponente | Technologie | Version |
|------------|-------------|---------|
| **Runtime** | Python | 3.11+ |
| **LLM-Server** | LM Studio | Latest |
| **LLM-Modell** | Qwen 2.5 | 3B-7B |
| **RAG-Framework** | LangChain | 0.1+ |
| **Vector DB** | ChromaDB | 0.4.18+ |
| **Frontend** | Streamlit | 1.28+ |
| **Embeddings** | sentence-transformers | 2.2+ |

---

## 📦 Installation

### 1. Python-Umgebung einrichten

```bash
# Virtual Environment erstellen
python -m venv venv

# Aktivieren
source venv/bin/activate  # macOS/Linux
# oder
venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt
```

### 2. LM Studio installieren

1. Download: https://lmstudio.ai/
2. Modell herunterladen: **Qwen 2.5 3B** oder **7B**
3. Server starten (Port 1234)

```bash
# Optional: CLI-Server
lms server start --model qwen2.5-3b-instruct
```

### 3. Projekt konfigurieren

```bash
# Config-Datei erstellen
cp config/config.example.yaml config/config.yaml

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
