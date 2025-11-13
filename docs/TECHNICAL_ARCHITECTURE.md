# Technische Architektur
## IFB PROFI - KI-gestützte Textverarbeitung

**Version:** 3.0 (Architektur-Varianten)  
**Stand:** 10. November 2025  
**Zielgruppe:** Entwickler-Team

---

## 🎯 ARCHITEKTUR-VARIANTEN

Das System kann in drei Komplexitätsstufen implementiert werden:

### **Option 1: Super-Lite** (Empfohlen für schnellen Start)
- **Ziel:** Funktionsfähiger MVP in 1 Woche
- **LLM:** LM Studio (inkl. RAG-Features)
- **RAG:** LM Studio Built-in Collections
- **Hosting:** Komplett lokal
- **Aufwand:** Minimal

### **Option 2: Lite** (Mehr Kontrolle)
- **Ziel:** Produktionsreife in 2-3 Wochen
- **LLM:** LM Studio (nur Inferenz)
- **RAG:** Eigenes System (ChromaDB + LangChain)
- **Hosting:** Lokal/Hybrid
- **Aufwand:** Mittel

### **Option 3: Full** (Enterprise)
- **Ziel:** Skalierbare Cloud-Lösung
- **LLM:** Eigenes Hosting (vLLM/Ollama)
- **RAG:** Full-Stack (ChromaDB/Weaviate + Custom Pipeline)
- **Hosting:** Cloud/Kubernetes
- **Aufwand:** Hoch

---

## 1. SYSTEM-ÜBERSICHT

## 1. SYSTEM-ÜBERSICHT

### Option 1: Super-Lite Architektur (Empfohlen für MVP)

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
│                     PYTHON BACKEND (Minimal)                     │
├──────────────────┬──────────────────┬──────────────────────────┤
│  DOKUMENT-HANDLER│  LM STUDIO API   │  KRITERIEN-ENGINE       │
│  • Upload        │   CONNECTOR      │  • Iterative Prüfung    │
│  • Speicherung   │   • HTTP Client  │  • Ergebnis-Sammlung    │
│  • Metadaten     │   • Error Handle │  • JSON-Speicherung     │
└──────────────────┴──────────────────┴──────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LM STUDIO (All-in-One)                          │
│  • LLM Hosting (Qwen 2.5 3B-7B)                                 │
│  • RAG Built-in (Document Collections)                          │
│  • Embeddings (Integriert)                                      │
│  • OpenAI-kompatible API                                        │
│  • GUI für Modell-Management                                    │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATENSPEICHERUNG                             │
│  • Lokales Dateisystem - Uploads & Projekte                     │
│  • JSON-Files - Metadaten & Ergebnisse                          │
│  • LM Studio Collections - RAG Dokumente                        │
└─────────────────────────────────────────────────────────────────┘
```

**Vorteile:**
- ✅ Schnellste Implementierung (1 Woche machbar)
- ✅ Minimale Komplexität
- ✅ Keine eigene RAG-Infrastruktur
- ✅ GUI für Nicht-Techniker
- ✅ Alles lokal, datenschutzkonform

**Nachteile:**
- ❌ Abhängig von LM Studio Features
- ❌ Weniger Kontrolle über RAG-Prozess
- ❌ Begrenzte Anpassbarkeit

---

### Option 2: Lite Architektur (Eigenes RAG)

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT WEB-INTERFACE                      │
│                    (Wizard-basierte UI)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  PYTHON BACKEND (Erweitert)                      │
├──────────────────┬──────────────────┬──────────────────────────┤
│  DOKUMENT-PARSER │   RAG-SYSTEM     │  KRITERIEN-ENGINE       │
│  • PDF/DOCX/XLSX │   • LangChain    │  • Iterative Prüfung    │
│  • Chunking      │   • ChromaDB     │  • RAG-Integration       │
│  • Metadaten     │   • Embeddings   │  • Validierung          │
└──────────────────┴──────────────────┴──────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  LM STUDIO (Nur LLM)                             │
│  • LLM Hosting (Qwen 2.5 7B)                                    │
│  • OpenAI-kompatible API                                        │
│  • Fokus auf Inferenz                                           │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATENSPEICHERUNG                             │
│  • ChromaDB - Vector Store (Embeddings)                         │
│  • Lokales Dateisystem - Projektdateien & Uploads               │
│  • JSON-Files - Projektmetadaten & Ergebnisse                   │
└─────────────────────────────────────────────────────────────────┘
```

**Vorteile:**
- ✅ Mehr Kontrolle über RAG
- ✅ Optimierbare Chunking-Strategie
- ✅ Eigene Metadaten-Verwaltung
- ✅ LLM weiterhin einfach (LM Studio)

**Nachteile:**
- ❌ Mehr Entwicklungsaufwand (2-3 Wochen)
- ❌ ChromaDB Setup & Wartung
- ❌ Eigene Embedding-Pipeline

---

### Option 3: Full Architektur (Enterprise)

```
┌─────────────────────────────────────────────────────────────────┐
│                  WEB-INTERFACE (React/Vue)                       │
│               (Multi-User, Authentifizierung)                    │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API GATEWAY / LOAD BALANCER                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  MICROSERVICES BACKEND                           │
├──────────────────┬──────────────────┬──────────────────────────┤
│  PARSER SERVICE  │   RAG SERVICE    │  INFERENCE SERVICE      │
│  • Scale on      │   • Weaviate/    │  • vLLM/TGI Hosting     │
│    Demand        │     Qdrant       │  • Load Balancing       │
│  • Queue System  │   • Custom       │  • GPU Cluster          │
│                  │     Embeddings   │                         │
└──────────────────┴──────────────────┴──────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                  DISTRIBUTED STORAGE                             │
│  • Vector DB Cluster (Weaviate/Qdrant)                          │
│  • Object Storage (S3/MinIO)                                    │
│  • PostgreSQL - Metadaten                                       │
│  • Redis - Caching                                              │
└─────────────────────────────────────────────────────────────────┘
```

**Vorteile:**
- ✅ Maximale Kontrolle
- ✅ Production-ready Skalierung
- ✅ Multi-User, Multi-Tenant
- ✅ High Availability

**Nachteile:**
- ❌ Hohe Komplexität
- ❌ Deutlich mehr Aufwand (Monate)
- ❌ Hardware-Anforderungen
- ❌ DevOps-Know-how erforderlich

---

## 2. TECH-STACK DETAILS

### 2.1 Variantenvergleich

| Komponente | Super-Lite | Lite | Full |
|------------|------------|------|------|
| **LLM Runtime** | LM Studio | LM Studio | vLLM/TGI |
| **LLM Modell** | Qwen 2.5 3B-7B | Qwen 2.5 7B | Qwen 2.5 14B+ |
| **RAG System** | LM Studio Built-in | LangChain + ChromaDB | Custom + Weaviate |
| **Vector DB** | LM Studio Collections | ChromaDB | Weaviate/Qdrant |
| **Embeddings** | LM Studio (automatisch) | HuggingFace Models | Custom Fine-tuned |
| **Frontend** | Streamlit | Streamlit | React/Vue |
| **Backend** | Python (Minimal) | Python + LangChain | FastAPI Microservices |
| **Deployment** | Lokal | Lokal/Docker | Kubernetes/Cloud |
| **Setup Zeit** | 1 Woche | 2-3 Wochen | 2-3 Monate |

---

### 2.2 Option 1: Super-Lite Setup

**Kernidee:** LM Studio übernimmt RAG, LLM-Hosting und API. Python nur für Business-Logik.

#### Tech-Stack
| Komponente | Technologie | Version | Zweck |
|------------|-------------|---------|-------|
| **LLM Server** | LM Studio | Latest | All-in-One (LLM + RAG) |
| **LLM Modell** | Qwen 2.5 3B | Latest | Schnelle Inferenz |
| **Runtime** | Python | 3.11+ | Backend-Logik |
| **Frontend** | Streamlit | 1.28+ | Web-Interface |
| **HTTP Client** | requests/httpx | Latest | LM Studio API Calls |

#### LM Studio Configuration

```python
# config.yaml (Super-Lite)
llm:
  provider: "lm_studio"
  base_url: "http://localhost:1234/v1"
  model: "qwen2.5-3b-instruct"
  use_builtin_rag: true  # Wichtig!
  
rag:
  provider: "lm_studio"  # Keine eigene Implementierung
  collection_name: "ifb_documents"

backend:
  document_handler: "simple"  # Nur Upload + Speicherung
  criteria_engine: "iterative"  # Sequential processing
```

#### Workflow Super-Lite

1. **Upload:** Python speichert Dokumente in `/data/projects/{id}/uploads/`
2. **Indexierung:** Python sendet Dokumente via API an LM Studio
3. **RAG:** LM Studio indexiert in eigener Collection
4. **Prüfung:** Python sendet Kriterien-Prompts mit RAG-Anfragen
5. **Antwort:** LM Studio liefert kontextbasierte Antworten
6. **Speicherung:** Python speichert Ergebnisse als JSON

**Beispiel: LM Studio API Call mit RAG**

```python
import requests

def check_criterion_superlite(criterion_prompt: str, project_id: str):
    """Kriterium mit LM Studio Built-in RAG prüfen"""
    
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        json={
            "model": "qwen2.5-3b-instruct",
            "messages": [
                {
                    "role": "system",
                    "content": "Du bist ein Förderantrag-Prüfer für IFB Hamburg."
                },
                {
                    "role": "user",
                    "content": criterion_prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 1000,
            # RAG-Aktivierung (LM Studio spezifisch)
            "collection": f"projekt_{project_id}",
            "use_rag": True,
            "top_k_chunks": 5
        }
    )
    
    return response.json()["choices"][0]["message"]["content"]
```

**Kritischer Punkt:** Prüfen, ob LM Studio diese RAG-Features bietet! Falls nicht → Option 1.5 (siehe unten).

---

### 2.3 Option 2: Lite Setup

**Kernidee:** LM Studio nur für LLM. Eigenes RAG mit ChromaDB + LangChain.

#### Tech-Stack
| Komponente | Technologie | Version | Zweck |
|------------|-------------|---------|-------|
| **LLM Server** | LM Studio | Latest | LLM Inferenz |
| **LLM Modell** | Qwen 2.5 7B | Latest | Hauptmodell |
| **RAG Framework** | LangChain | 0.1+ | RAG-Pipeline |
| **Vector DB** | ChromaDB | 0.4.18+ | Embeddings-Speicher |
| **Embeddings** | HuggingFace | - | multilingual-e5-large |
| **Runtime** | Python | 3.11+ | Backend-Sprache |
| **Frontend** | Streamlit | 1.28+ | Web-Interface |

#### Configuration

```python
# config.yaml (Lite)
llm:
  provider: "lm_studio"
  base_url: "http://localhost:1234/v1"
  model: "qwen2.5-7b-instruct"
  
rag:
  provider: "chromadb"  # Eigenes System
  persist_directory: "./data/chromadb"
  embedding_model: "intfloat/multilingual-e5-large"
  chunk_size: 1000
  chunk_overlap: 200
  
backend:
  document_parser: "full"  # PDF/DOCX/XLSX Parser
  criteria_engine: "rag_enhanced"  # Mit eigenem RAG
```

#### RAG-System Setup

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma
from openai import OpenAI

# Embeddings
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

# Vector Store
vectorstore = Chroma(
    collection_name=f"projekt_{projekt_id}",
    embedding_function=embeddings,
    persist_directory="./data/chromadb"
)

# LLM Client (LM Studio)
llm_client = OpenAI(
    base_url="http://localhost:1234/v1",
    api_key="not-needed"
)

def check_criterion_lite(criterion_prompt: str, projekt_id: str):
    """Kriterium mit eigenem RAG prüfen"""
    
    # 1. Relevante Chunks via ChromaDB finden
    docs = vectorstore.similarity_search(
        criterion_prompt,
        k=5
    )
    
    # 2. Kontext zusammenstellen
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # 3. LLM-Anfrage mit Kontext
    response = llm_client.chat.completions.create(
        model="qwen2.5-7b-instruct",
        messages=[
            {
                "role": "system",
                "content": "Du bist ein Förderantrag-Prüfer für IFB Hamburg."
            },
            {
                "role": "user",
                "content": f"Kontext:\n{context}\n\nAufgabe:\n{criterion_prompt}"
            }
        ],
        temperature=0.3,
        max_tokens=1000
    )
    
    return response.choices[0].message.content
```

---

### 2.4 Option 3: Full Setup

**Kernidee:** Komplette Eigenentwicklung mit Cloud-Readiness.

#### Tech-Stack
| Komponente | Technologie | Version | Zweck |
|------------|-------------|---------|-------|
| **LLM Runtime** | vLLM | Latest | Production LLM Serving |
| **LLM Modell** | Qwen 2.5 14B | Latest | Größeres Modell |
| **RAG Framework** | Custom | - | Optimierte Pipeline |
| **Vector DB** | Weaviate | Latest | Enterprise Vector DB |
| **Embeddings** | Custom Fine-tuned | - | Domain-spezifisch |
| **API Gateway** | FastAPI | Latest | Microservices |
| **Frontend** | React | 18+ | Modern Web UI |
| **Queue System** | Redis/RabbitMQ | Latest | Async Processing |
| **Database** | PostgreSQL | 15+ | Metadaten |
| **Deployment** | Kubernetes | 1.28+ | Orchestration |

**Hinweis:** Option 3 ist für dieses Projekt überdimensioniert. Nur bei Multi-Tenant-Anforderungen sinnvoll.

---

### 2.5 Option 1.5: Super-Lite ohne LM Studio RAG

Falls LM Studio keine RAG-Features bietet, hier die Hybrid-Lösung:

**Kernidee:** LM Studio nur für LLM. Minimales RAG mit ChromaDB (vereinfacht).

```python
# Minimales RAG (kein LangChain!)
from chromadb import Client
from sentence_transformers import SentenceTransformer

# Simple Embedding Model
embedder = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

# ChromaDB (einfach)
chroma_client = Client()
collection = chroma_client.create_collection(f"projekt_{projekt_id}")

# Dokumente indexieren
def index_document(text: str, metadata: dict):
    chunks = simple_chunk(text, size=1000)  # Einfache Chunking-Funktion
    embeddings = embedder.encode(chunks)
    
    collection.add(
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=[metadata] * len(chunks),
        ids=[f"chunk_{i}" for i in range(len(chunks))]
    )

# RAG Retrieval
def retrieve_context(query: str, top_k=5):
    query_embedding = embedder.encode([query])
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k
    )
    return results['documents'][0]
```

**Vorteil:** Immer noch sehr einfach, aber volle Kontrolle über RAG.

---

### 2.6 Dokumenten-Parser (Alle Varianten)

**Parser sind variantenunabhängig** - Alle drei Optionen nutzen dieselbe Parser-Infrastruktur.

**Unterstützte Formate:**

| Format | Library | Verwendung | Komplexität |
|--------|---------|------------|-------------|
| **PDF** | PyMuPDF (fitz) | Projektskizze, Gutachten | Mittel |
| **DOCX** | python-docx | Word-Dokumente, Vorlagen | Einfach |
| **XLSX** | openpyxl | Kalkulationen, Finanzübersichten | Einfach |

**Hinweis:** Super-Lite kann mit vereinfachtem Parsing starten (nur Text), Lite/Full nutzen volle Features.

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
                "tables": list[dict]      # Extrahierte Tabellen (optional)
            }
        """
        pass
```

**Details:** Siehe `02_DOCUMENT_PARSING.md`

---

### 2.7 Datenspeicherung

**Speicher-Strategie nach Variante:**

| Komponente | Super-Lite | Lite | Full |
|------------|------------|------|------|
| **Vector Store** | LM Studio | ChromaDB | Weaviate/Qdrant |
| **Projektdateien** | Lokales FS | Lokales FS | S3/MinIO |
| **Metadaten** | JSON | JSON | PostgreSQL |
| **Caching** | - | - | Redis |

**Dateistruktur (Super-Lite & Lite):**

```
data/
├── chromadb/                    # Vector Store (nur Lite)
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
│   │       ├── criteria_check.json
│   │       └── report.md
│   └── projekt_002/
│       └── ...
│
└── regelwerke/                  # Förderrichtlinien (optional)
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
  "architecture_variant": "super_lite",
  "documents": [
    {
      "doc_id": "doc_001",
      "doc_type": "projektskizze",
      "filename": "projektskizze.pdf",
      "uploaded_at": "2024-10-31T10:05:00Z",
      "parsed": true,
      "indexed_in_rag": true
    }
  ]
}
```

---

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
---

## 3. EMPFEHLUNG & ENTSCHEIDUNGSHILFE

### Für dieses Projekt: **Option 1.5 (Super-Lite mit minimalem RAG)**

**Begründung:**
1. **LM Studio RAG-Features unsicher** - Nicht alle Versionen bieten vollwertige RAG-APIs
2. **Volle Kontrolle über RAG** - Kriterienkatalog benötigt präzise Chunk-Auswahl
3. **Schnell umsetzbar** - Minimales ChromaDB + sentence-transformers (keine LangChain)
4. **Einfach wartbar** - Weniger Dependencies, klarer Code
5. **Upgrade-fähig** - Später einfach zu Lite/Full erweiterbar

### Konkrete Stack-Empfehlung

```yaml
# config/system_config.yaml (Empfohlen)

llm:
  provider: "lm_studio"
  base_url: "http://localhost:1234/v1"
  model: "qwen2.5-7b-instruct"  # 7B für bessere Qualität
  temperature: 0.3
  max_tokens: 2000

rag:
  provider: "chromadb"
  persist_directory: "./data/chromadb"
  embedding_model: "paraphrase-multilingual-MiniLM-L12-v2"  # Kompakt & schnell
  chunk_size: 1000
  chunk_overlap: 200
  top_k: 5

parser:
  pdf: "pymupdf"
  docx: "python-docx"
  xlsx: "openpyxl"
  
storage:
  projects_dir: "./data/projects"
  uploads_subdir: "uploads"
  extracted_subdir: "extracted"
  results_subdir: "results"
```

### Minimale Dependencies (requirements.txt)

```txt
# LLM & RAG
openai==1.3.0              # OpenAI-Client für LM Studio API
chromadb==0.4.18           # Vector Database
sentence-transformers==2.2.2  # Embeddings (kein HuggingFace overhead)

# Document Parsing
pymupdf==1.23.8            # PDF
python-docx==1.1.0         # DOCX
openpyxl==3.1.2            # XLSX

# Frontend
streamlit==1.28.0          # UI

# Utils
pydantic==2.5.0            # Validierung
python-dotenv==1.0.0       # Config
```

**Geschätzte Entwicklungszeit:** 5-7 Tage für MVP

---

## 4. IMPLEMENTIERUNGS-ROADMAP

### Phase 1: Fundament (Tag 1-2)

**Ziel:** Basis-Setup funktionsfähig

- [x] Projektstruktur anlegen
- [ ] Config-System (`config/system_config.yaml`)
- [ ] LM Studio installieren & testen
- [ ] Python Environment & Dependencies
- [ ] Minimale Streamlit-App (Hello World)

**Testkriterium:** LM Studio antwortet auf API-Call

### Phase 2: Dokumenten-Upload & Parsing (Tag 2-3)

**Ziel:** Dokumente hochladen und parsen

- [ ] Streamlit Upload-Komponente
- [ ] PDF-Parser (nur Text-Extraktion)
- [ ] Speicherung in `/data/projects/{id}/uploads/`
- [ ] JSON-Export des geparsten Texts

**Testkriterium:** PDF hochladen → Text extrahiert → JSON gespeichert

### Phase 3: Minimales RAG-System (Tag 3-4)

**Ziel:** Dokumente indexieren und suchen

- [ ] ChromaDB Setup & Initialisierung
- [ ] Embedding-Model laden (sentence-transformers)
- [ ] Simple Chunking-Funktion
- [ ] Indexierungs-Pipeline
- [ ] Test: Dokument indexieren → Similarity Search funktioniert

**Testkriterium:** Query "Hamburg Standort" findet relevante Chunks

### Phase 4: LLM-Integration & Kriterien-Engine (Tag 4-5)

**Ziel:** Erste Kriterien-Prüfung automatisiert

- [ ] LM Studio API-Client (OpenAI-kompatibel)
- [ ] Kriterien-Katalog laden (`config/criteria_catalog.json`)
- [ ] Iterative Prüfung (ein Kriterium nach dem anderen)
- [ ] RAG + LLM kombinieren
- [ ] Ergebnis als JSON speichern

**Testkriterium:** Kriterium "Projektort" wird korrekt geprüft

### Phase 5: Vollständiger Wizard (Tag 5-6)

**Ziel:** Kompletter User-Flow

- [ ] Seite 1: Projekt anlegen
- [ ] Seite 2: Dokumente hochladen
- [ ] Seite 3: Automatische Prüfung (mit Progress)
- [ ] Seite 4: Ergebnisübersicht
- [ ] Navigation zwischen Seiten

**Testkriterium:** Vollständiger Durchlauf von Projekt-Anlage bis Ergebnis

### Phase 6: Polishing & Reports (Tag 6-7)

**Ziel:** Production-ready MVP

- [ ] Error-Handling verbessern
- [ ] Loading-States & Progress-Bars
- [ ] Export-Funktionen (JSON, Markdown)
- [ ] Terminal-Logging (siehe DEVELOPMENT_PRINCIPLES.md)
- [ ] Dokumentation vervollständigen

**Testkriterium:** Demo mit echten IFB-Dokumenten läuft durch

---

## 5. MIGRATIONS-PFADE

### Von Super-Lite zu Lite

**Änderungen:**
1. LangChain installieren
2. RAG-Code auf LangChain-Abstractions umstellen
3. Bessere Chunking-Strategie (RecursiveCharacterTextSplitter)
4. Eigene Embedding-Pipeline

**Aufwand:** 2-3 Tage

### Von Lite zu Full

**Änderungen:**
1. Backend zu FastAPI umbauen
2. LM Studio → vLLM/TGI
3. ChromaDB → Weaviate/Qdrant
4. Streamlit → React Frontend
5. Docker/Kubernetes Setup

**Aufwand:** 3-4 Wochen

**Empfehlung:** Nur bei echten Production-Anforderungen (Multi-User, Skalierung)

---

**Ende der Technischen Architektur**

**Nächste Schritte:**
- Siehe `SYSTEM_REQUIREMENTS.md` für Hardware-Details
- Siehe `03_RAG_SYSTEM.md` für RAG-Implementierung
- Siehe `04_LLM_INTEGRATION.md` für LLM-Setup

Bei Fragen: Siehe README.md oder kontaktiert das Team!

