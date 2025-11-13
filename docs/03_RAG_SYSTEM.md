# RAG System
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 3.0 (Architektur-Varianten)  
**Stand:** 10. November 2025

---

## 🎯 ÜBERSICHT

RAG (Retrieval-Augmented Generation) System für intelligente Dokumentenanalyse und kontextbasierte LLM-Antworten.

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

### Option 1: Super-Lite (LM Studio Built-in RAG)

**Konzept:** LM Studio übernimmt RAG vollständig.

**Voraussetzung:** LM Studio muss RAG-Features unterstützen (zu prüfen!).

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
- ChromaDB (Vector Store)
- sentence-transformers (Embeddings)
- Einfache Python-Funktionen

#### Komponenten

**1. ChromaDB Setup**
```python
import chromadb
from chromadb.config import Settings

class SimpleRAG:
    """Minimales RAG-System ohne LangChain"""
    
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
    """Einfache Chunking-Funktion ohne LangChain"""
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
    """Dokument indexieren"""
    
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
    """Relevante Chunks finden"""
    
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
- ❌ Etwas mehr Code als Option 1
- ❌ Eigene ChromaDB-Verwaltung

---

### Option 2: Lite (LangChain + ChromaDB)

**Konzept:** Production-ready RAG mit bewährten Tools.

**Tech-Stack:**
- LangChain (Framework)
- ChromaDB (Vector Store)
- HuggingFace Embeddings

#### Komponenten
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

### 3. Embeddings
**Zweck:** Text in numerische Vektoren umwandeln für Similarity-Search

#### Empfohlene Modelle
**Option 1: BAAI/bge-large-en-v1.5** (Bisherige Wahl)
- Größe: 335M Parameter
- Dimensionen: 1024
- Sprachen: Primär Englisch (funktioniert aber auch mit Deutsch)
- Performance: Sehr gut für technische Texte

**Option 2: intfloat/multilingual-e5-large** (Besseres Deutsch)
- Größe: 560M Parameter
- Dimensionen: 1024
- Sprachen: 100+ Sprachen inkl. Deutsch
- Performance: Exzellent für mehrsprachige Dokumente

**Option 3: Qwen2.5-Embeddings** (Beste Integration)
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

### 4. Metadaten-Extraktion
**Zweck:** Zusätzliche Informationen für präzisere Suche

#### Standard-Metadaten pro Chunk
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

### Phase 1: Indexierung (nach Dokument-Upload)

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
```

#### Implementierung
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

### Phase 2: Retrieval (bei Kriterienprüfung)

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
└─────────────────────────────────────────────────┘
```

#### Implementierung
```python
def retrieve_relevant_chunks(projekt_id: str, query: str, top_k: int = 5):
    """Findet relevante Chunks für eine Anfrage"""
    
    # 1. Collection laden
    collection = chromadb_client.get_collection(
        name=f"projekt_{projekt_id}"
    )
    
    # 2. Query vektorisieren
    query_embedding = embedding_model.embed_query(query)
    
    # 3. Similarity Search
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"projekt_id": projekt_id}  # Filter nach Projekt
    )
    
    # 4. Ergebnisse formatieren
    chunks = []
    for i in range(len(results['documents'][0])):
        chunks.append({
            'text': results['documents'][0][i],
            'metadata': results['metadatas'][0][i],
            'similarity': results['distances'][0][i],
            'source': results['metadatas'][0][i]['filename']
        })
    
    return chunks
```

---

## 🎯 KRITERIEN-SPEZIFISCHE RETRIEVAL-STRATEGIE

### Sukzessives Prüfen (ein Kriterium nach dem anderen)

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

*...und so weiter für K003-K006*

### Optimierung: Adaptive Query-Expansion

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

### Collection-Struktur

**Eine Collection pro Projekt:**
```
chromadb/
├── projekt_abc123/
│   ├── chunks (37 Einträge)
│   ├── embeddings (37x1024 Vektoren)
│   └── metadata.json
├── projekt_def456/
│   ├── chunks (42 Einträge)
│   ├── embeddings (42x1024 Vektoren)
│   └── metadata.json
└── ...
```

**Vorteile:**
- Isolation zwischen Projekten
- Einfaches Löschen (drop_collection)
- Parallele Verarbeitung möglich
- Keine Cross-Projekt-Kontamination

### Performance-Optimierung

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

---

## 🔧 BEST PRACTICES

### 1. Chunk-Size Tuning
**Testen verschiedener Größen:**
```python
CHUNK_CONFIGS = [
    {'size': 500, 'overlap': 100},
    {'size': 1000, 'overlap': 200},
    {'size': 1500, 'overlap': 300},
]

for config in CHUNK_CONFIGS:
    precision, recall = evaluate_chunking(config)
    print(f"Size {config['size']}: P={precision:.2f}, R={recall:.2f}")
```

### 2. Qualitätskontrolle
```python
def validate_indexing(projekt_id: str):
    """Prüfe Indexierungs-Qualität"""
    
    collection = get_collection(projekt_id)
    
    # Test-Queries mit bekannten Antworten
    test_cases = [
        ("Projektstandort", "sollte 'Hamburg' enthalten"),
        ("Unternehmensgründung", "sollte Datum enthalten"),
    ]
    
    for query, expected in test_cases:
        chunks = retrieve_relevant_chunks(projekt_id, query, top_k=3)
        assert any(expected in chunk['text'] for chunk in chunks), \
            f"Query '{query}' fand nicht '{expected}'"
```

### 3. Duplicate Detection
```python
import hashlib

def detect_duplicate_chunks(chunks: list) -> list:
    """Entferne identische Chunks"""
    
    seen_hashes = set()
    unique_chunks = []
    
    for chunk in chunks:
        chunk_hash = hashlib.md5(chunk.encode()).hexdigest()
        
        if chunk_hash not in seen_hashes:
            seen_hashes.add(chunk_hash)
            unique_chunks.append(chunk)
    
    removed = len(chunks) - len(unique_chunks)
    print(f"⚠️ {removed} Duplikate entfernt")
    
    return unique_chunks
```

---

## 🔍 INTEGRATION MIT LLM

### Kontext-Augmentation

**Prompt-Template für Kriterienprüfung:**
```python
def build_augmented_prompt(kriterium: dict, chunks: list) -> str:
    """Erstelle Prompt mit RAG-Kontext"""
    
    # Kontext aus relevanten Chunks
    context = "\n\n---\n\n".join([
        f"[Quelle: {chunk['source']}, Seite {chunk['metadata']['page_number']}]\n{chunk['text']}"
        for chunk in chunks[:3]  # Top 3
    ])
    
    # Vollständiger Prompt
    prompt = f"""Du bist ein Experte für Förderkriterien der IFB Hamburg.

AUFGABE:
Prüfe anhand der folgenden Dokumente das Kriterium:
"{kriterium['titel']}"

ZIEL:
{kriterium['ziel']}

RELEVANTE DOKUMENT-AUSZÜGE:
{context}

ANLEITUNG:
{kriterium['prompt']}

Antworte im JSON-Format:
{{
    "erfuellt": true/false,
    "wert": "Extrahierter Wert",
    "begruendung": "Detaillierte Begründung",
    "confidence": 0.95,
    "quellen": ["Quelle 1", "Quelle 2"]
}}
"""
    
    return prompt
```

### Retrieval-Qualität messen

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