# RAG System
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 4.0 (Option 1 MVP + Future Features)  
**Stand:** 10. November 2025

---

## 🎯 ÜBERSICHT

RAG (Retrieval-Augmented Generation) System für intelligente Dokumentenanalyse und kontextbasierte LLM-Antworten.

> **Docling-Update (Dez 2025)**
> - Parser & Chunking basieren ausschließlich auf Docling-Blöcken (PDF/DOCX/XLSX) mit Bounding Boxes.
> - Jeder Chunk speichert `bbox`, `page_width`, `page_height`, `docling_id`, `table_md` (falls Tabelle).
> - Hybrid Chunking: Docling-Blöcke zuerst, bei Token-Überschreitung sekundärer Split mit geerbter BBox.
> - Vector Store wird mit Schema-Version `docling-v1` neu aufgebaut (automatische Rekreation bei Mismatch).

### Was ist RAG?

RAG kombiniert die Stärken von **Informationsabruf** und **Textgenerierung**:

1. **Indexierung**: Dokumente werden in kleine Chunks (Textabschnitte) zerlegt
2. **Vektorisierung**: Jeder Chunk wird in einen hochdimensionalen Vektor umgewandelt (Embedding)
3. **Speicherung**: Vektoren werden in Vector Database mit Metadaten gespeichert
4. **Retrieval**: Bei einer Anfrage wird diese ebenfalls vektorisiert und ähnliche Chunks werden gefunden
5. **Augmentation**: Die relevanten Chunks werden als Kontext an das LLM übergeben
6. **Generation**: Das LLM generiert eine Antwort basierend auf dem bereitgestellten Kontext

### Vorteile für das IFB-Projekt

✅ **Aktualität** - Arbeitet mit aktuellen Förderrichtlinien ohne Model-Retraining  
✅ **Nachvollziehbarkeit** - Jede Antwort kann auf konkrete Dokumentstellen zurückgeführt werden  
✅ **Flexibilität** - Neue Dokumente können jederzeit hinzugefügt werden  
✅ **Datenschutz** - Alles läuft lokal ohne externe APIs  
✅ **Skalierbarkeit** - Tausende Dokumente effizient durchsuchbar

---

## 🏗️ RAG-VARIANTEN

### ⚠️ Option 1 (NICHT EMPFOHLEN): Super-Lite (LM Studio Built-in RAG)

**Konzept:** LM Studio übernimmt RAG vollständig.

**Voraussetzung:** LM Studio muss RAG-Features unterstützen (zu prüfen!).

**Status:** ⚠️ Zu prüfen ob LM Studio diese APIs bietet! Falls nicht verfügbar → Option 1.5

---

### ✅ Option 1.5 (EMPFOHLEN für MVP): Super-Lite mit minimalem RAG

**Konzept:** LM Studio nur für LLM. Minimales eigenes RAG ohne LangChain.

**Tech-Stack:**
- ChromaDB (Vector Store)
- sentence-transformers (Embeddings)
- Einfache Python-Funktionen

**DIES IST DIE OPTION FÜR OPTION 1 MVP!**

#### Workflow
```
Dokument → LM Studio API → Automatische Indexierung → RAG-Collection
Query → LM Studio API (mit RAG-Parameter) → Kontextbasierte Antwort
```

#### Implementierung
```python
import requests

def index_document_superlite(document_path: str, projekt_id: str):
    """Dokument via LM Studio API indexieren"""
    
    with open(document_path, 'rb') as f:
        response = requests.post(
            "http://localhost:1234/v1/documents",
            files={'file': f},
            data={'collection': f'projekt_{projekt_id}'}
        )
    
    return response.json()

def query_with_rag_superlite(query: str, projekt_id: str):
    """Query mit LM Studio Built-in RAG"""
    
    response = requests.post(
        "http://localhost:1234/v1/chat/completions",
        json={
            "model": "qwen2.5-7b-instruct",
            "messages": [{"role": "user", "content": query}],
            "collection": f'projekt_{projekt_id}',
            "use_rag": True,
            "top_k_chunks": 5
        }
    )
    
    return response.json()['choices'][0]['message']['content']
```

**Vorteile:**
- ✅ Minimaler Code
- ✅ Keine eigene Vector DB
- ✅ LM Studio übernimmt Komplexität

**Nachteile:**
- ❌ Abhängig von LM Studio Features
- ❌ Weniger Kontrolle über Chunking
- ❌ Unklar ob alle Features verfügbar

**Status:** ⚠️ Zu prüfen ob LM Studio diese APIs bietet!

---

### Option 1.5: Super-Lite mit minimalem RAG (EMPFOHLEN)

**Konzept:** LM Studio nur für LLM. Minimales eigenes RAG ohne LangChain.

**Tech-Stack:**
**Tech-Stack:**
- ChromaDB (Vector Store)
- sentence-transformers (Embeddings)
- Einfache Python-Funktionen

**DIES IST DIE OPTION FÜR OPTION 1 MVP!**

#### Komponenten - ✅ OPTION 1

**1. ChromaDB Setup**
```python
import chromadb
from chromadb.config import Settings

class SimpleRAG:
    """Minimales RAG-System ohne LangChain - OPTION 1"""
    
    def __init__(self, persist_dir: str = "./data/chromadb"):
        self.client = chromadb.Client(Settings(
            persist_directory=persist_dir,
            anonymized_telemetry=False
        ))
        self.embedder = None
    
    def initialize_embedder(self):
        """Lade Embedding-Modell"""
        from sentence_transformers import SentenceTransformer
        self.embedder = SentenceTransformer(
            'paraphrase-multilingual-MiniLM-L12-v2'
        )
    
    def create_collection(self, projekt_id: str):
        """Erstelle Collection für Projekt"""
        return self.client.get_or_create_collection(
            name=f"projekt_{projekt_id}",
            metadata={"projekt_id": projekt_id}
        )
```

**2. Einfaches Chunking**
```python
def simple_chunk(text: str, chunk_size: int = 1000, overlap: int = 200):
    """Einfache Chunking-Funktion ohne LangChain - OPTION 1"""
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # An Satzende aufhören wenn möglich
        if end < len(text):
            last_period = chunk.rfind('. ')
            if last_period > chunk_size * 0.7:  # Mindestens 70% der Chunk-Größe
                end = start + last_period + 1
                chunk = text[start:end]
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks
```

**3. Indexierung**
```python
def index_document(self, text: str, projekt_id: str, metadata: dict):
    """Dokument indexieren - OPTION 1"""
    
    # Collection holen
    collection = self.create_collection(projekt_id)
    
    # Chunking
    chunks = simple_chunk(text, chunk_size=1000, overlap=200)
    
    # Embeddings generieren
    embeddings = self.embedder.encode(chunks, show_progress_bar=True)
    
    # In ChromaDB speichern
    collection.add(
        documents=chunks,
        embeddings=embeddings.tolist(),
        metadatas=[metadata] * len(chunks),
        ids=[f"{metadata['doc_id']}_chunk_{i}" for i in range(len(chunks))]
    )
    
    print(f"✓ {len(chunks)} Chunks indexiert für Projekt {projekt_id}")
```

**4. Retrieval**
```python
def retrieve_context(self, query: str, projekt_id: str, top_k: int = 5):
    """Relevante Chunks finden - OPTION 1"""
    
    collection = self.client.get_collection(f"projekt_{projekt_id}")
    
    # Query vektorisieren
    query_embedding = self.embedder.encode([query])
    
    # Similarity Search
    results = collection.query(
        query_embeddings=query_embedding.tolist(),
        n_results=top_k
    )
    
    return {
        'chunks': results['documents'][0],
        'metadatas': results['metadatas'][0],
        'distances': results['distances'][0]
    }
```

**Vorteile:**
- ✅ Volle Kontrolle über RAG
- ✅ Immer noch sehr einfach
- ✅ Keine LangChain-Overhead
- ✅ Funktioniert garantiert

**Nachteile:**
- ❌ Etwas mehr Code als LM Studio Built-in
- ❌ Eigene ChromaDB-Verwaltung

---

### ⚠️ Option 2+ (NICHT in MVP): Lite (LangChain + ChromaDB)

**Konzept:** Production-ready RAG mit bewährten Tools.

**Tech-Stack:**
- LangChain (Framework)
- ChromaDB (Vector Store)
- HuggingFace Embeddings

#### Komponenten - ⚠️ OPTION 2+

### 2. Text-Splitting - ⚠️ OPTION 2+

**Zweck:** Dokumente in sinnvolle, durchsuchbare Einheiten zerlegen

#### Chunk-Größen (Empfehlungen)
- **Förderrichtlinien**: 1000-1500 Tokens (detaillierter Kontext wichtig)
- **Projektskizzen**: 750-1000 Tokens (Balance zwischen Detail und Übersicht)
- **Checklisten**: 500-750 Tokens (kürzere, präzise Informationen)

#### Overlap-Strategie
- **20-30% Überlappung** zwischen Chunks
- Verhindert Kontextverlust an Chunk-Grenzen
- Beispiel: Bei 1000 Tokens → 200 Tokens Overlap

#### Chunk-Grenzen
**Priorität (von hoch nach niedrig):**
1. Kapitelgrenzen (H1, H2, etc.)
2. Absatzgrenzen (`\n\n`)
3. Satzgrenzen (`. `)
4. Wortgrenzen (` `)

**Implementierung:**
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    separators=["\n\n", "\n", ". ", " ", ""],
    length_function=len
)

chunks = text_splitter.split_text(document_text)
```

### 3. Embeddings - ⚠️ OPTION 2+

**Zweck:** Text in numerische Vektoren umwandeln für Similarity-Search

**In Option 1: Verwenden wir paraphrase-multilingual-MiniLM-L12-v2**

**Option 2+ bietet mehr Auswahl:**

#### Empfohlene Modelle
**Option 1: BAAI/bge-large-en-v1.5**
- Größe: 335M Parameter
- Dimensionen: 1024
- Sprachen: Primär Englisch (funktioniert aber auch mit Deutsch)
- Performance: Sehr gut für technische Texte

**Option 2: intfloat/multilingual-e5-large**
- Größe: 560M Parameter
- Dimensionen: 1024
- Sprachen: 100+ Sprachen inkl. Deutsch
- Performance: Exzellent für mehrsprachige Dokumente

**Option 3: Qwen2.5-Embeddings**
- Eigenes Embedding-Modell von Qwen
- Native Integration mit Qwen-LLM
- Optimiert für asiatische UND europäische Sprachen

**Implementierung:**
```python
from langchain.embeddings import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-large",
    model_kwargs={'device': 'cpu'},  # oder 'cuda'/'mps'
    encode_kwargs={'normalize_embeddings': True}
)

# Batch-Processing für Performance
texts = [chunk1, chunk2, chunk3, ...]
vectors = embeddings.embed_documents(texts)
```

### 4. Metadaten-Extraktion - ⚠️ OPTION 2+

**Zweck:** Zusätzliche Informationen für präzisere Suche

**In Option 1: Nur minimale Metadaten (Dateiname, Dokumenttyp)**

#### Standard-Metadaten pro Chunk (Option 2+)
```python
chunk_metadata = {
    # Dokument-Identifikation
    "projekt_id": "projekt_abc123",
    "document_id": "doc_xyz789",
    "document_type": "projektskizze",  # oder "projektantrag"
    "filename": "projektskizze.pdf",
    
    # Positions-Informationen
    "chunk_index": 3,
    "page_number": 2,
    "section": "3. Technologischer Lösungsansatz",
    
    # Zeitstempel
    "indexed_at": "2025-11-10T14:30:00Z",
    "document_version": "1.0",
    
    # Qualitätsindikatoren
    "char_count": 1245,
    "token_count": 1050,
    "has_tables": False,
    "has_images": False
}
```

---

## 🔄 PROZESSABLAUF

### ✅ OPTION 1 - Vereinfachter Ablauf

### Phase 1: Indexierung (nach Dokument-Upload) - ✅ OPTION 1

```
┌─────────────────────────────────────────────────┐
│  1. Dokumente hochgeladen                       │
│     - projektskizze.pdf                         │
│     - projektantrag.docx                        │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  2. Parsing & Textextraktion                    │
│     → Siehe 02_DOCUMENT_PARSING.md              │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  3. Chunking                                    │
│     - Projektskizze: 12 Chunks                  │
│     - Projektantrag: 25 Chunks                  │
│     - Total: 37 Chunks                          │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  4. Embedding-Generierung                       │
│     - Batch-Processing: 37 Embeddings          │
│     - Dauer: ~2-3 Sekunden                     │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  5. ChromaDB-Speicherung                        │
│     - Collection: projekt_abc123                │
│     - 37 Vektoren mit Metadaten                 │
│     - Persistiert auf Disk                      │
└─────────────────────────────────────────────────┘
### Phase 1: Indexierung (nach Dokument-Upload) - ✅ OPTION 1

```
┌─────────────────────────────────────────────────┐
│  1. Dokumente hochgeladen                       │
│     - projektskizze.pdf                         │
│     - projektantrag.docx                        │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  2. Parsing & Textextraktion                    │
│     → parse_document() - Einfache Funktion      │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  3. Chunking                                    │
│     → simple_chunk() - Feste Größe 1000 Zeichen│
│     - Projektskizze: 12 Chunks                  │
│     - Projektantrag: 25 Chunks                  │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  4. Embedding-Generierung                       │
│     → sentence-transformers encode()            │
│     - Batch-Processing: 37 Embeddings          │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  5. ChromaDB-Speicherung                        │
│     - Collection: projekt_abc123                │
│     - 37 Vektoren mit Mini-Metadaten            │
└─────────────────────────────────────────────────┘
```

#### Implementierung - ✅ OPTION 1
```python
def index_project_documents_simple(projekt_id: str, documents: list):
    """Indexiert alle Dokumente eines Projekts - OPTION 1"""
    
    # SimpleRAG initialisieren
    rag = SimpleRAG()
    rag.initialize_embedder()
    
    for document in documents:
        # 1. Text extrahieren
        text = parse_document(document.path)["volltext"]
        
        # 2. Einfaches Chunking
        chunks = simple_chunk(text, chunk_size=1000, overlap=200)
        
        # 3. Indexieren mit minimalen Metadaten
        rag.index_document(
            text=text,
            projekt_id=projekt_id,
            metadata={
                'doc_id': document.id,
                'dokumenttyp': document.type,
                'dateiname': document.filename
            }
        )
    
    print(f"✅ Projekt {projekt_id} indexiert")
```

---

### ⚠️ OPTION 2+ - Detaillierter Ablauf mit LangChain

**Implementierung (LangChain):**
```python
def index_project_documents(projekt_id: str, documents: list):
    """Indexiert alle Dokumente eines Projekts in ChromaDB"""
    
    # 1. ChromaDB Collection erstellen
    collection = chromadb_client.get_or_create_collection(
        name=f"projekt_{projekt_id}"
    )
    
    all_chunks = []
    all_metadatas = []
    
    for document in documents:
        # 2. Text extrahieren (siehe 02_DOCUMENT_PARSING.md)
        text = parse_document(document.path)
        
        # 3. In Chunks aufteilen
        chunks = text_splitter.split_text(text)
        
        # 4. Metadaten pro Chunk erstellen
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk)
            all_metadatas.append({
                "projekt_id": projekt_id,
                "document_id": document.id,
                "document_type": document.type,
                "chunk_index": i,
                "filename": document.filename
            })
    
    # 5. Embeddings generieren (batch)
    embeddings = embedding_model.embed_documents(all_chunks)
    
    # 6. In ChromaDB speichern
    collection.add(
        documents=all_chunks,
        embeddings=embeddings,
        metadatas=all_metadatas,
        ids=[f"chunk_{i}" for i in range(len(all_chunks))]
    )
    
    print(f"✅ {len(all_chunks)} Chunks indexiert für Projekt {projekt_id}")
```

### Phase 2: Retrieval (bei Kriterienprüfung) - ✅ OPTION 1

```
┌─────────────────────────────────────────────────┐
│  1. Kriterium K001: Projektort Hamburg         │
│     Query: "Betriebsstätte Hamburg Standort"   │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  2. Query-Embedding generieren                  │
│     query_vector = embed("Betriebsstätte...")   │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  3. Similarity Search in ChromaDB               │
│     - Vergleich mit allen 37 Chunks             │
│     - Cosine Similarity berechnen               │
│     - Top 5 relevanteste Chunks finden          │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  4. Relevante Chunks zurückgeben                │
│     Chunk #17: "...Hamburg, Beispielstr. 1..."  │
│     Chunk #3:  "...Unternehmensstandort..."     │
│     Chunk #22: "...Betriebsstätte seit 2020..." │
│     (Similarity: 0.92, 0.87, 0.81)              │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  5. Kontext an LLM übergeben                    │
│     Prompt + Top 3 Chunks → LLM → Bewertung    │
### Phase 2: Retrieval (bei Kriterienprüfung) - ✅ OPTION 1

```
┌─────────────────────────────────────────────────┐
│  1. Kriterium K001: Projektort Hamburg         │
│     Query: "Betriebsstätte Hamburg Standort"   │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  2. Query-Embedding generieren                  │
│     query_vector = embedder.encode(query)       │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  3. Similarity Search in ChromaDB               │
│     collection.query() - Top 5 Chunks           │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  4. Relevante Chunks zurückgeben                │
│     Chunk #17: "...Hamburg, Beispielstr. 1..."  │
│     Chunk #3:  "...Unternehmensstandort..."     │
│     Chunk #22: "...Betriebsstätte seit 2020..." │
└─────────────────┬───────────────────────────────┘
                  ↓
┌─────────────────────────────────────────────────┐
│  5. Kontext an LM Studio LLM übergeben          │
│     Prompt + Top 5 Chunks → LLM → Bewertung    │
└─────────────────────────────────────────────────┘
```

#### Implementierung - ✅ OPTION 1
```python
def retrieve_relevant_chunks_simple(projekt_id: str, query: str, top_k: int = 5):
    """Findet relevante Chunks für eine Anfrage - OPTION 1"""
    
    rag = SimpleRAG()
    rag.initialize_embedder()
    
    # Retrieval
    results = rag.retrieve_context(query, projekt_id, top_k)
    
    # Einfache Formatierung
    return results['chunks']
```

---

## 🎯 KRITERIEN-SPEZIFISCHE RETRIEVAL-STRATEGIE - ✅ OPTION 1 + ⚠️ OPTION 2+

### Sukzessives Prüfen (ein Kriterium nach dem anderen) - ✅ OPTION 1

Jedes der 6 Kriterien wird **einzeln und nacheinander** geprüft:

#### Kriterium K001: Projektort Hamburg
```python
query_k001 = """
Betriebsstätte Hamburg Standort Adresse Handelsregister 
Firmensitz Unternehmensstandort Geschäftsadresse
"""

chunks = retrieve_relevant_chunks(projekt_id, query_k001, top_k=5)
result_k001 = llm_check_kriterium(chunks, criteria_prompt_k001)
```

#### Kriterium K002: Unternehmensalter
```python
query_k002 = """
Gründungsdatum Unternehmensgründung Handelsregister 
Geschäftstätigkeit seit bestehend Firmenjahre
"""

chunks = retrieve_relevant_chunks(projekt_id, query_k002, top_k=5)
result_k002 = llm_check_kriterium(chunks, criteria_prompt_k002)
```

Jedes der 6 Kriterien wird **einzeln und nacheinander** geprüft:

#### Kriterium K001: Projektort Hamburg - ✅ OPTION 1
```python
query_k001 = "Betriebsstätte Hamburg Standort Adresse"

chunks = retrieve_relevant_chunks_simple(projekt_id, query_k001, top_k=5)
result_k001 = llm_check_kriterium(chunks, criteria_prompt_k001)
```

#### Kriterium K002: Unternehmensalter - ✅ OPTION 1
```python
query_k002 = "Gründungsdatum Unternehmensgründung Handelsregister"

chunks = retrieve_relevant_chunks_simple(projekt_id, query_k002, top_k=5)
result_k002 = llm_check_kriterium(chunks, criteria_prompt_k002)
```

*...und so weiter für K003-K006*

---

### ⚠️ OPTION 2+: Optimierung mit Adaptive Query-Expansion

Wenn Konfidenz niedrig ist (<75%), automatisch nachprüfen:

```python
def adaptive_retrieval(projekt_id: str, kriterium: dict, initial_result: dict):
    """Erweiterte Suche bei niedriger Konfidenz"""
    
    if initial_result['confidence'] < 0.75:
        # Erweitere Query mit Synonymen/verwandten Begriffen
        expanded_query = expand_query(kriterium['query'])
        
        # Zweite Suche mit mehr Results
        additional_chunks = retrieve_relevant_chunks(
            projekt_id, 
            expanded_query, 
            top_k=10
        )
        
        # LLM erneut prüfen mit mehr Kontext
        return llm_check_kriterium(additional_chunks, kriterium['prompt'])
    
    return initial_result
```

---

## 📊 DATENHALTUNG & PERFORMANCE

### Collection-Struktur - ✅ OPTION 1

**Eine Collection pro Projekt:**
```
chromadb/
├── projekt_abc123/
│   ├── chunks (37 Einträge)
│   ├── embeddings (37x384 Vektoren)
│   └── metadata.json
├── projekt_def456/
│   ├── chunks (42 Einträge)
│   ├── embeddings (42x384 Vektoren)
│   └── metadata.json
└── ...
```

**Vorteile:**
- Isolation zwischen Projekten
- Einfaches Löschen (drop_collection)
- Keine Cross-Projekt-Kontamination

---

### ⚠️ OPTION 2+: Performance-Optimierung

#### 1. Batch-Processing
```python
# ❌ Schlecht: Ein Embedding pro Anfrage
for chunk in chunks:
    embedding = model.embed_documents([chunk])

# ✅ Gut: Alle Embeddings auf einmal
embeddings = model.embed_documents(chunks)
```

#### 2. Caching
```python
# Cache für bereits indexierte Dokumente
INDEXED_DOCUMENTS = {}

def is_already_indexed(document_hash: str) -> bool:
    return document_hash in INDEXED_DOCUMENTS

def mark_as_indexed(document_hash: str, chunk_count: int):
    INDEXED_DOCUMENTS[document_hash] = {
        'indexed_at': datetime.now(),
        'chunk_count': chunk_count
    }
```

#### 3. Incremental Updates
```python
def update_document(projekt_id: str, document_id: str, new_version: str):
    """Update nur geänderter Dokumente"""
    
    # 1. Alte Chunks löschen
    collection.delete(where={"document_id": document_id})
    
    # 2. Neue Chunks indexieren
    new_chunks = parse_and_chunk(new_version)
    add_to_collection(new_chunks)
```

### Storage-Anforderungen

**Durchschnittliches Projekt:**
- 2 Dokumente
- ~40 Chunks total
- ~40 KB pro Chunk (Text + Embedding + Metadata)
- **~1.6 MB pro Projekt**

**1000 Projekte ≈ 1.6 GB Storage**

### ⚠️ OPTION 2+: Performance-Optimierung

**In Option 1: Kein Caching, keine incremental updates, kein paralleles Processing**

#### 1. Batch-Processing
```python
# ❌ Schlecht: Ein Embedding pro Anfrage
for chunk in chunks:
    embedding = model.embed_documents([chunk])

# ✅ Gut: Alle Embeddings auf einmal
embeddings = model.embed_documents(chunks)
```

#### 2. Caching
```python
# Cache für bereits indexierte Dokumente
INDEXED_DOCUMENTS = {}

def is_already_indexed(document_hash: str) -> bool:
    return document_hash in INDEXED_DOCUMENTS

def mark_as_indexed(document_hash: str, chunk_count: int):
    INDEXED_DOCUMENTS[document_hash] = {
        'indexed_at': datetime.now(),
        'chunk_count': chunk_count
    }
```

#### 3. Incremental Updates
```python
def update_document(projekt_id: str, document_id: str, new_version: str):
    """Update nur geänderter Dokumente"""
    
    # 1. Alte Chunks löschen
    collection.delete(where={"document_id": document_id})
    
    # 2. Neue Chunks indexieren
    new_chunks = parse_and_chunk(new_version)
    add_to_collection(new_chunks)
```

---

### Storage-Anforderungen - ✅ OPTION 1

**Durchschnittliches Projekt:**
- 2 Dokumente
- ~40 Chunks total
- ~20 KB pro Chunk (Text + Embedding + Metadata)
- **~800 KB pro Projekt**

**1000 Projekte ≈ 800 MB Storage**

---

## 🔧 BEST PRACTICES

### ⚠️ OPTION 2+: Chunk-Size Tuning, Qualitätskontrolle, Duplicate Detection

**In Option 1: Feste Chunk-Größe 1000 Zeichen, keine erweiterte QS**

---

## 🔍 INTEGRATION MIT LLM - ✅ OPTION 1 + ⚠️ OPTION 2+

### Kontext-Augmentation - ✅ OPTION 1

**Prompt-Template für Kriterienprüfung:**
```python
def build_augmented_prompt_simple(kriterium: dict, chunks: list) -> str:
    """Erstelle Prompt mit RAG-Kontext - OPTION 1"""
    
    # Kontext aus relevanten Chunks (einfach)
    context = "\n\n---\n\n".join(chunks[:5])  # Top 5
    
    # Vollständiger Prompt
    prompt = f"""Du bist ein Experte für Förderkriterien der IFB Hamburg.

AUFGABE:
Prüfe anhand der folgenden Dokumente das Kriterium:
"{kriterium['titel']}"

RELEVANTE DOKUMENT-AUSZÜGE:
{context}

ANLEITUNG:
{kriterium['prompt']}

Antworte im JSON-Format:
{{
    "erfuellt": true/false,
    "wert": "Extrahierter Wert",
    "begruendung": "Detaillierte Begründung"
}}
"""
    
    return prompt
```

---

### ⚠️ OPTION 2+: Retrieval-Qualität messen

**Erweiterte Metriken und Evaluation**

```python
def measure_retrieval_quality(projekt_id: str, test_queries: list):
    """Evaluiere Retrieval-Performance"""
    
    results = []
    
    for query, expected_chunks in test_queries:
        # Retrieval durchführen
        retrieved = retrieve_relevant_chunks(projekt_id, query, top_k=5)
        retrieved_ids = {c['metadata']['chunk_index'] for c in retrieved}
        
        # Precision & Recall
        relevant = set(expected_chunks)
        precision = len(retrieved_ids & relevant) / len(retrieved_ids)
        recall = len(retrieved_ids & relevant) / len(relevant)
        
        results.append({
            'query': query,
            'precision': precision,
            'recall': recall,
            'f1': 2 * (precision * recall) / (precision + recall)
        })
    
    avg_f1 = sum(r['f1'] for r in results) / len(results)
    print(f"📊 Average F1-Score: {avg_f1:.2f}")
    
    return results
```

---

## ❓ OFFENE FRAGEN & NÄCHSTE SCHRITTE

### Zu klären mit IFB
1. **Versionierung**: Wie werden Updates von Förderrichtlinien gehandhabt?
2. **Sprachen**: Nur Deutsch oder auch Englisch für EU-Förderungen?
3. **Archivierung**: Wie lange werden alte Versionen vorgehalten?
4. **Zugriffsrechte**: Gibt es dokumentenspezifische Berechtigungen?
5. **Audit-Trail**: Muss nachvollziehbar sein, wer wann welches Dokument hochgeladen hat?

### Implementierungs-Schritte
1. ✅ **Proof of Concept**: Basis-RAG mit 2-3 Beispieldokumenten
2. ⏳ **Chunk-Size Evaluation**: Verschiedene Größen mit IFB-Dokumenten testen
3. ⏳ **Embedding-Model Vergleich**: BGE vs. Multilingual-E5 vs. Qwen-Embeddings
4. ⏳ **Retrieval-Benchmarking**: Precision/Recall für alle 6 Kriterien messen
5. ⏳ **Integration**: RAG in 7-Schritte-Wizard-Pipeline einbauen

---

## 📚 VERWANDTE DOKUMENTE

- **Dokumenten-Parsing:** `02_DOCUMENT_PARSING.md`
- **LLM-Integration:** `04_LLM_INTEGRATION.md`
- **Kriterien-Engine:** `05_CRITERIA_ENGINE.md`
- **UI-Flow:** `01_UI_FLOW.md`

---

**Ende der RAG-System Dokumentation**