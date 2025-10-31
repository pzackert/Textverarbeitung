# Technische Architektur
## IFB PROFI - KI-gestützte Textverarbeitung

**Version:** 2.0 (aktualisiert mit LM Studio)  
**Stand:** 31. Oktober 2024  
**Zielgruppe:** Entwickler-Team

---

## 1. SYSTEM-ÜBERSICHT

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT WEB-INTERFACE                      │
│                    (Wizard-basierte UI)                          │
│  • Projekt anlegen                                               │
│  • Dokumente hochladen                                           │
│  • Status-Tracking                                               │
│  • Reports & Checklisten                                         │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     BACKEND (Python + LangChain)                 │
├──────────────────┬──────────────────┬──────────────────────────┤
│  DOKUMENT-PARSER │   RAG-SYSTEM     │  REGELWERK-ENGINE       │
│  • PDF-Extraktion│   • Embeddings   │  • Fördervoraussetzungen│
│  • DOCX-Parsing  │   • ChromaDB     │  • Bewertungskriterien  │
│  • XLSX-Parsing  │   • LLM-Retrieval│  • Konsistenzprüfung   │
└──────────────────┴──────────────────┴──────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     LM STUDIO (Lokales LLM)                      │
│  • Qwen 2.5 (3-7B) - Hauptmodell                                │
│  • CLI-Anbindung verfügbar                                       │
│  • Läuft auf M1 Mac / Consumer Hardware                         │
│  • Kein Cloud-Upload, 100% lokal                                │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATENSPEICHERUNG                             │
├─────────────────────────────────────────────────────────────────┤
│  • ChromaDB - Vector Store (Embeddings)                         │
│  • Lokales Dateisystem - Projektdateien & Uploads               │
│  • JSON-Files - Projektmetadaten & Ergebnisse                   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     OUTPUT-GENERIERUNG                           │
│  • Checklisten (JSON/Markdown)                                  │
│  • Bewertungsreports (Markdown/PDF)                             │
│  • Use-Case-spezifische Checks                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. TECH-STACK DETAILS

### 2.1 Core Technologies

| Komponente | Technologie | Version | Zweck |
|------------|-------------|---------|-------|
| **Runtime** | Python | 3.11+ | Backend-Sprache |
| **LLM-Server** | **LM Studio** | Latest | Lokales LLM-Hosting |
| **LLM-Modell** | **Qwen 2.5** | 3B-7B | Hauptmodell für Inferenz |
| **RAG-Framework** | LangChain | 0.1+ | RAG-Pipeline |
| **Vector DB** | ChromaDB | 0.4.18+ | Embeddings-Speicher |
| **Frontend** | Streamlit | 1.28+ | Web-Interface |
| **Embeddings** | sentence-transformers | 2.2+ | Multilingual Embeddings |

### 2.2 LM Studio Setup

**Warum LM Studio statt Ollama?**
- ✅ Benutzerfreundlichere GUI
- ✅ Einfachere Modell-Verwaltung
- ✅ CLI-Support für Automatisierung
- ✅ Bessere Performance auf Consumer-Hardware (M1 Mac getestet!)
- ✅ Direkter API-Kompatibilität (OpenAI-Format)

**Installation & Modelle:**

```bash
# 1. LM Studio herunterladen
# https://lmstudio.ai/

# 2. Empfohlene Modelle:
# - Qwen 2.5 3B (schnell, 3-5 GB RAM)
# - Qwen 2.5 7B (besser, 6-8 GB RAM)
# - Llama 3.2 3B (Alternative)

# 3. CLI-Server starten (falls benötigt)
lms server start --model qwen2.5-3b-instruct
```

**API-Anbindung (Python):**

```python
import requests

class LMStudioClient:
    """Wrapper für LM Studio API (OpenAI-kompatibel)."""
    
    def __init__(self, base_url: str = "http://localhost:1234/v1"):
        self.base_url = base_url
    
    def generate(
        self,
        prompt: str,
        system_prompt: str = None,
        temperature: float = 0.3,
        max_tokens: int = 2048
    ) -> str:
        """Generiert Text mit LM Studio."""
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = requests.post(
            f"{self.base_url}/chat/completions",
            json={
                "model": "local-model",
                "messages": messages,
                "temperature": temperature,
                "max_tokens": max_tokens
            }
        )
        response.raise_for_status()
        
        return response.json()["choices"][0]["message"]["content"]
```

### 2.3 Dokumenten-Parser

**Unterstützte Formate:**

| Format | Library | Verwendung |
|--------|---------|------------|
| **PDF** | PyMuPDF (fitz) | Projektskizze, Beschreibung, Gutachten |
| **DOCX** | python-docx | Word-Dokumente, Vorlagen |
| **XLSX** | openpyxl | Kalkulationen, Finanzübersichten |

**Parser-Architektur:**

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any

class BaseParser(ABC):
    """Abstract Base Class für alle Parser."""
    
    @abstractmethod
    def parse(self, file_path: Path) -> Dict[str, Any]:
        """
        Parst Datei und extrahiert strukturierte Daten.
        
        Returns:
            {
                "text": str,              # Volltext
                "metadata": dict,         # Titel, Datum, Autor
                "structured_data": dict,  # Strukturierte Felder
                "tables": list[dict]      # Extrahierte Tabellen
            }
        """
        pass
```

### 2.4 RAG-System mit LangChain

**Pipeline-Komponenten:**

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from langchain.chains import RetrievalQA

# 1. Text Splitting
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""]
)

# 2. Embeddings (Multilingual)
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# 3. Vector Store (ChromaDB)
vectorstore = Chroma(
    collection_name="ifb_documents",
    embedding_function=embeddings,
    persist_directory="./data/chromadb"
)

# 4. Retrieval
retriever = vectorstore.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}
)

# 5. LLM-Integration (LM Studio)
from langchain.llms import OpenAI  # OpenAI-kompatibel!

llm = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed",
    temperature=0.3
)

# 6. RAG Chain
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,
    return_source_documents=True
)
```

### 2.5 Datenspeicherung

**Keine MongoDB - Stattdessen:**

1. **ChromaDB** - Für Vektoren & Embeddings
2. **Lokales Dateisystem** - Für Projektdateien
3. **JSON-Files** - Für Metadaten & Ergebnisse

**Dateistruktur:**

```
data/
├── chromadb/                    # Vector Store
│   └── chroma.sqlite3
│
├── projects/                    # Projektdaten
│   ├── projekt_001/
│   │   ├── metadata.json       # Projekt-Metadaten
│   │   ├── uploads/            # Hochgeladene Dateien
│   │   │   ├── projektskizze.pdf
│   │   │   ├── kalkulation.xlsx
│   │   │   └── ...
│   │   ├── extracted/          # Geparste Daten
│   │   │   ├── projektskizze.json
│   │   │   └── kalkulation.json
│   │   └── results/            # Prüfungsergebnisse
│   │       ├── foerdervoraussetzungen.json
│   │       ├── bewertung.json
│   │       └── checkliste.md
│   └── projekt_002/
│       └── ...
│
└── regelwerke/                  # Förderrichtlinien
    ├── profi_foerderrichtlinie.pdf
    └── bewertungskriterien.yaml
```

**Beispiel metadata.json:**

```json
{
  "projekt_id": "projekt_001",
  "projekt_name": "Vollautomatische Verpackungsmaschine",
  "antragsteller": "Verpackungsmaschinenbau GmbH",
  "modul": "PROFI Standard",
  "status": "in_review",
  "created_at": "2024-10-31T10:00:00Z",
  "updated_at": "2024-10-31T14:30:00Z",
  "documents": [
    {
      "doc_id": "doc_001",
      "doc_type": "projektskizze",
      "filename": "projektskizze.pdf",
      "uploaded_at": "2024-10-31T10:05:00Z",
      "parsed": true,
      "vector_ids": ["chunk_001", "chunk_002", "..."]
    }
  ]
}
```

---

## 3. WIZARD-FLOW (7 Schritte)

### Schritt 1: Projekt anlegen
- Input: Projektname, Antragsteller, Modul
- Output: Neues Projekt in `data/projects/projekt_XXX/`

### Schritt 2: Dokumente hochladen
- Input: PDF, DOCX, XLSX-Dateien
- Output: Dateien in `uploads/` gespeichert

### Schritt 3: Dokumenten-Parsing
- Prozess: Parser für jeden Dateityp
- Output: JSON-Files in `extracted/`

### Schritt 4: Informationsextraktion (RAG)
- Prozess: 
  1. Text chunken
  2. Embeddings erstellen
  3. In ChromaDB speichern
  4. LLM-basierte Extraktion strukturierter Daten
- Output: Strukturierte Daten in `metadata.json`

### Schritt 5: Fördervoraussetzungen prüfen
- Prozess: Use-Case-spezifische Checks via RAG + LLM
- Output: `foerdervoraussetzungen.json` + Checkliste

### Schritt 6: Bewertung
- Prozess: 5 Bewertungskriterien scoring
- Output: `bewertung.json`

### Schritt 7: Report generieren
- Output: Markdown-Report oder PDF

---

## 4. USE-CASE-SPEZIFISCHE CHECKS

**Ansatz:** Pro Dokumententyp definierte Checks

**Beispiel: KMU-Erklärung prüfen**

```python
class KMUCheck:
    """Prüft KMU-Status aus KMU-Erklärung."""
    
    def __init__(self, rag_retriever, llm_client):
        self.retriever = rag_retriever
        self.llm = llm_client
    
    def check_mitarbeiter(self, projekt_id: str) -> dict:
        """Prüft: Mitarbeiterzahl < 250."""
        
        # 1. RAG: Relevante Dokument-Chunks holen
        docs = self.retriever.retrieve(
            query="Mitarbeiterzahl Anzahl Beschäftigte",
            filters={"projekt_id": projekt_id, "doc_type": "kmu_erklaerung"}
        )
        
        # 2. LLM: Extrahiere Mitarbeiterzahl
        prompt = f"""Extrahiere die Mitarbeiterzahl aus folgendem Text:

{docs[0].content}

Antworte nur mit einer Zahl, z.B.: 45"""
        
        response = self.llm.generate(prompt, temperature=0.1)
        mitarbeiter = int(response.strip())
        
        # 3. Check
        return {
            "kriterium": "Mitarbeiterzahl < 250",
            "wert": mitarbeiter,
            "erfuellt": mitarbeiter < 250,
            "begruendung": f"Das Unternehmen hat {mitarbeiter} Mitarbeiter."
        }
    
    def check_jahresumsatz(self, projekt_id: str) -> dict:
        """Prüft: Jahresumsatz ≤ 50 Mio. EUR."""
        # Analog zu check_mitarbeiter
        pass
    
    def check_bilanzsumme(self, projekt_id: str) -> dict:
        """Prüft: Bilanzsumme ≤ 43 Mio. EUR."""
        # Analog
        pass
    
    def run_all_checks(self, projekt_id: str) -> dict:
        """Führt alle KMU-Checks durch."""
        return {
            "mitarbeiter": self.check_mitarbeiter(projekt_id),
            "jahresumsatz": self.check_jahresumsatz(projekt_id),
            "bilanzsumme": self.check_bilanzsumme(projekt_id)
        }
```

**Checklisten-Output (Markdown):**

```markdown
# KMU-Status Prüfung

## Projektskizze: Verpackungsmaschinenbau GmbH

| Kriterium | Wert | Grenzwert | Status | Begründung |
|-----------|------|-----------|--------|------------|
| Mitarbeiterzahl | 45 | < 250 | ✅ Erfüllt | Unternehmen hat 45 Mitarbeiter |
| Jahresumsatz | 8,5 Mio. € | ≤ 50 Mio. € | ✅ Erfüllt | Umsatz liegt unter Grenzwert |
| Bilanzsumme | 6,2 Mio. € | ≤ 43 Mio. € | ✅ Erfüllt | Bilanzsumme unter Grenzwert |

**Ergebnis:** KMU-Status bestätigt ✅
```

---

## 5. REGELWERK-ENGINE

**Fördervoraussetzungen als YAML:**

```yaml
# data/regelwerke/foerdervoraussetzungen.yaml

foerdervoraussetzungen:
  - id: projektort
    name: "Projektort in Hamburg"
    typ: boolean
    bedingung: "Betriebsstätte muss in Hamburg sein"
    quellen:
      - handelsregisterauszug
      - projektbeschreibung
    check_prompt: |
      Prüfe anhand der Dokumente: Hat das Unternehmen eine Betriebsstätte in Hamburg?
      Antworte nur mit "Ja" oder "Nein" und einer kurzen Begründung.
  
  - id: unternehmensalter
    name: "Etabliertes Unternehmen"
    typ: numeric
    bedingung: "Gegründet vor mindestens 3 Jahren"
    quellen:
      - handelsregisterauszug
    check_prompt: |
      Extrahiere das Gründungsjahr des Unternehmens.
      Berechne: Ist das Unternehmen mindestens 3 Jahre alt?
      Antworte im JSON-Format: {"gruendungsjahr": YYYY, "alter_jahre": X, "erfuellt": true/false}
  
  # ... weitere Voraussetzungen
```

**Check-Engine:**

```python
import yaml
from pathlib import Path

class FoerdervoraussetzungenEngine:
    """Lädt Regelwerk und führt Checks durch."""
    
    def __init__(self, regelwerk_path: Path, rag_retriever, llm_client):
        with open(regelwerk_path) as f:
            self.regelwerk = yaml.safe_load(f)
        self.retriever = rag_retriever
        self.llm = llm_client
    
    def check_voraussetzung(self, voraussetzung_id: str, projekt_id: str) -> dict:
        """Führt Check für eine Fördervoraussetzung durch."""
        
        # 1. Regelwerk laden
        regel = next(
            r for r in self.regelwerk["foerdervoraussetzungen"]
            if r["id"] == voraussetzung_id
        )
        
        # 2. Relevante Dokumente holen
        docs = self.retriever.retrieve(
            query=regel["name"],
            filters={
                "projekt_id": projekt_id,
                "doc_type": regel["quellen"]
            }
        )
        
        # 3. LLM-Check
        context = "\n\n".join([d.content for d in docs[:3]])
        prompt = f"{regel['check_prompt']}\n\nKontext:\n{context}"
        
        response = self.llm.generate(prompt, temperature=0.1)
        
        # 4. Ergebnis parsen und zurückgeben
        return {
            "voraussetzung": regel["name"],
            "erfuellt": "ja" in response.lower() or "true" in response.lower(),
            "antwort": response,
            "quellen": [d.source for d in docs]
        }
```

---

## 6. ERWEITERUNGEN (Optional)

### 6.1 MCP-Server-Integration

Falls ihr MCP (Model Context Protocol) nutzen wollt:

```python
# Beispiel: MCP-Server für Datenbankzugriff

from mcp import MCPServer

mcp_server = MCPServer("ifb-database")

@mcp_server.tool()
def get_projekt_info(projekt_id: str) -> dict:
    """Holt Projektinformationen aus dem Dateisystem."""
    metadata_path = f"data/projects/{projekt_id}/metadata.json"
    with open(metadata_path) as f:
        return json.load(f)

# In LangChain einbinden
from langchain.tools import Tool

tools = [
    Tool(
        name="get_projekt_info",
        func=mcp_server.get_tool("get_projekt_info"),
        description="Holt Projektinformationen"
    )
]
```

### 6.2 Visualisierungen (Plotly)

```python
import plotly.graph_objects as go

def create_bewertung_chart(bewertung: dict) -> go.Figure:
    """Erstellt Radar-Chart für Bewertungskriterien."""
    
    categories = [
        "Produktidee",
        "Innovationsgrad",
        "Team",
        "Vermarktung",
        "Arbeitsplatz/Umwelt"
    ]
    
    values = [
        bewertung["produktidee"]["score"],
        bewertung["innovationsgrad"]["score"],
        bewertung["team"]["score"],
        bewertung["vermarktung"]["score"],
        bewertung["arbeitsplatz_umwelt"]["score"]
    ]
    
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Bewertung'
    ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=False,
        title="Bewertungsprofil"
    )
    
    return fig
```

---

## 7. DEPLOYMENT

### 7.1 Lokale Entwicklung

```bash
# 1. Repository klonen
git clone <your-repo>
cd ifb-profi-ki

# 2. Virtual Environment
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Dependencies
pip install -r requirements.txt

# 4. LM Studio starten (GUI oder CLI)
# - GUI: LM Studio öffnen → Modell laden → Server starten
# - CLI: lms server start

# 5. ChromaDB initialisieren
python scripts/init_chromadb.py

# 6. Streamlit starten
streamlit run frontend/streamlit_app.py
```

### 7.2 Requirements.txt

```txt
# Core
python>=3.11

# LLM & RAG
langchain==0.1.0
chromadb==0.4.18
sentence-transformers==2.2.2
openai==1.3.0  # Für LM Studio API (OpenAI-kompatibel)

# Document Parsing
PyMuPDF==1.23.8
python-docx==1.1.0
openpyxl==3.1.2

# Frontend
streamlit==1.28.2
plotly==5.18.0
streamlit-aggrid==0.3.4

# Data Validation
pydantic==2.5.2
pyyaml==6.0.1

# Utilities
python-dotenv==1.0.0
loguru==0.7.2
requests==2.31.0

# Testing
pytest==7.4.3
pytest-cov==4.1.0
```

---

## 8. PROJEKTSTRUKTUR

```
ifb-profi-ki/
├── backend/
│   ├── parsers/
│   │   ├── __init__.py
│   │   ├── base_parser.py
│   │   ├── pdf_parser.py
│   │   ├── docx_parser.py
│   │   └── xlsx_parser.py
│   │
│   ├── rag/
│   │   ├── __init__.py
│   │   ├── embeddings.py
│   │   ├── vector_store.py
│   │   ├── retriever.py
│   │   └── lm_studio_client.py
│   │
│   ├── rules/
│   │   ├── __init__.py
│   │   ├── foerdervoraussetzungen.py
│   │   ├── kmu_check.py
│   │   └── bewertung.py
│   │
│   └── utils/
│       ├── __init__.py
│       ├── config.py
│       └── logger.py
│
├── frontend/
│   ├── streamlit_app.py
│   └── pages/
│       ├── 1_Projekt_anlegen.py
│       ├── 2_Dokumente_hochladen.py
│       ├── 3_Parsing.py
│       ├── 4_Extraktion.py
│       ├── 5_Foerdervoraussetzungen.py
│       ├── 6_Bewertung.py
│       └── 7_Report.py
│
├── data/
│   ├── chromadb/
│   ├── projects/
│   └── regelwerke/
│       ├── foerdervoraussetzungen.yaml
│       └── profi_foerderrichtlinie.pdf
│
├── tests/
│   ├── test_parsers.py
│   ├── test_rag.py
│   └── test_rules.py
│
├── scripts/
│   ├── init_chromadb.py
│   └── setup.sh
│
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── pyproject.toml
```

---

## 9. PERFORMANCE & HARDWARE

### 9.1 Getestet auf M1 Mac

**Hardware:**
- MacBook Pro M1
- 16 GB RAM
- macOS Sonoma

**Modell:** Qwen 2.5 3B Instruct

**Performance:**
- Parsing: ~2-3 Sek/Dokument
- Embedding: ~1 Sek/1000 Tokens
- LLM-Inferenz: ~20-30 Tokens/Sek
- Gesamtdurchlauf (1 Projekt): ~2-3 Minuten

### 9.2 Empfehlungen

| Hardware | Empfohlenes Modell | Performance |
|----------|-------------------|-------------|
| M1/M2 Mac (8-16GB) | Qwen 2.5 3B | Gut |
| M1/M2 Mac (16-32GB) | Qwen 2.5 7B | Sehr gut |
| Windows/Linux (16GB RAM) | Qwen 2.5 3B | Gut |
| Windows/Linux (32GB RAM + GPU) | Qwen 2.5 7B | Sehr gut |

---

## 10. NÄCHSTE SCHRITTE

### Phase 1: Setup (diese Woche)
- [ ] Git-Repo erstellen
- [ ] Projektstruktur aufbauen
- [ ] LM Studio installieren & Qwen 2.5 laden
- [ ] requirements.txt & Python-Environment

### Phase 2: Basis-Features (nächste 2 Wochen)
- [ ] PDF/DOCX/XLSX-Parser implementieren
- [ ] ChromaDB-Integration
- [ ] LM Studio API-Client
- [ ] Erste Streamlit-Seiten

### Phase 3: RAG & Checks (Woche 3-4)
- [ ] RAG-Pipeline mit LangChain
- [ ] Use-Case-spezifische Checks
- [ ] Regelwerk-Engine
- [ ] Checklisten-Generierung

### Phase 4: UI & Reports (Woche 5-6)
- [ ] Vollständiger Wizard
- [ ] Visualisierungen
- [ ] Report-Generierung
- [ ] Testing & Polishing

---

**Ende der Technischen Architektur**

Bei Fragen: Siehe README.md oder kontaktiert das Team!
