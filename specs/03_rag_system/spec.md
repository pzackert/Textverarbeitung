# Phase 3: RAG System Specification

## 1. Überblick
Das RAG (Retrieval-Augmented Generation) System ist das Kernstück der IFB PROFI Plattform. Es ermöglicht die intelligente Verarbeitung und Abfrage von IFB-Dokumenten, indem es relevante Textabschnitte (Chunks) basierend auf einer Benutzeranfrage findet und diese einem lokalen LLM als Kontext bereitstellt. Dies garantiert, dass Antworten auf tatsächlichen Dokumenteninhalten basieren und nicht auf Halluzinationen.

**Rolle im Gesamtsystem:**
- Bindeglied zwischen Phase 2 (Parser) und Phase 4 (Criteria Engine).
- Stellt sicher, dass alle Daten lokal verarbeitet werden (Offline-First).
- Ermöglicht die Prüfung von Anträgen gegen komplexe Regelwerke.

## 2. Komponenten-Architektur

### 2.1 Chunker (Text-Splitting)
- **Funktion**: Zerlegt `Document`-Objekte in semantische `Chunk`-Objekte.
- **Logik**: Überlappende Fenster, Respektierung von Satz- und Absatzgrenzen.

### 2.2 Embeddings (Vector Generation)
- **Funktion**: Wandelt Text-Chunks in numerische Vektoren um.
- **Modell**: `sentence-transformers` (lokal).

### 2.3 Vector Store (ChromaDB)
- **Funktion**: Speichert Vektoren und Metadaten persistent.
- **Logik**: Effiziente Ähnlichkeitssuche (ANN).

### 2.4 Retriever (Similarity Search)
- **Funktion**: Findet die relevantesten Chunks für eine Query.
- **Logik**: Cosine Similarity + Metadaten-Filterung.

### 2.5 LLM Chain (Prompt + Response)
- **Funktion**: Orchestriert den Ablauf: Query -> Retrieve -> Prompt -> LLM -> Antwort.
- **Logik**: Prompt Engineering für deutschen Kontext.

## 3. Technologie-Stack
- **Vector Database**: `chromadb` (Lokal, persistent)
- **Embeddings**: `sentence-transformers` (Modell: `paraphrase-multilingual-MiniLM-L12-v2`)
- **LLM Interface**: `ollama` (via HTTP API)
- **Data Handling**: `pydantic` (Models), `numpy`

## 4. Datenfluss
1.  **Ingestion**: `Parser` -> `Document` -> `Chunker` -> `Chunks` -> `Embedding Service` -> `Vectors` -> `ChromaDB`.
2.  **Retrieval**: `User Query` -> `Embedding Service` -> `Query Vector` -> `ChromaDB` -> `Relevant Chunks`.
3.  **Generation**: `Relevant Chunks` + `User Query` + `System Prompt` -> `LLM` -> `Antwort`.

## 5. Konfiguration
Parameter in `config.yaml`:
- `chunk_size`: 500 Tokens
- `chunk_overlap`: 50 Tokens
- `embedding_model`: Name des HuggingFace Modells
- `top_k`: Anzahl der abzurufenden Chunks (Default: 5)
- `similarity_threshold`: Mindest-Score für Relevanz (Default: 0.7)

## 6. Abhängigkeiten
- **Input**: Validierte `Document`-Objekte aus Phase 2.
- **Runtime**: Laufender Ollama-Server mit `qwen2.5` Modellen.

## 7. Erfolgs-Kriterien
- [ ] **Ingestion**: PDF/DOCX/XLSX können in ChromaDB indexiert werden.
- [ ] **Retrieval**: Relevante Chunks werden für Test-Fragen gefunden (Recall > 0.8).
- [ ] **Generation**: LLM antwortet korrekt auf Deutsch basierend auf dem Kontext.
- [ ] **Offline**: Keine externen API-Calls.
- [ ] **Performance**: Retrieval < 200ms.
