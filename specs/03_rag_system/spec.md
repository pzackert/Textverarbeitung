# Phase 3: RAG System Specification

## 1. Overview
The RAG (Retrieval-Augmented Generation) System is the core intelligence engine of the IFB PROFI platform. It bridges the gap between raw document data (extracted in Phase 2) and the LLM's reasoning capabilities. Its primary purpose is to retrieve relevant context from local IFB documents and provide it to the LLM to answer user queries or validate criteria accurately, ensuring all data remains offline and privacy-compliant.

## 2. Core Components

### 2.1 Document Processor (Chunker)
- **Responsibility**: Splits `Document` objects from Phase 2 into semantically meaningful `Chunk` objects.
- **Key Logic**: Overlapping sliding windows, respecting sentence/paragraph boundaries.

### 2.2 Vector Store (ChromaDB)
- **Responsibility**: Stores embeddings and metadata for efficient similarity search.
- **Key Logic**: Persists data locally in `data/chromadb/`.

### 2.3 Embedding Service
- **Responsibility**: Converts text chunks into vector representations.
- **Key Logic**: Uses local HuggingFace models (via `sentence-transformers`).

### 2.4 Retriever
- **Responsibility**: Finds the most relevant chunks for a given query.
- **Key Logic**: Semantic search (Cosine Similarity) + Metadata Filtering.

### 2.5 RAG Chain (Orchestrator)
- **Responsibility**: Coordinates the flow: Query -> Retrieve -> Prompt -> LLM -> Response.
- **Key Logic**: Prompt engineering, context assembly, LLM interaction.

## 3. Technology Stack
- **Vector Database**: `chromadb` (Local, persistent)
- **Embeddings**: `sentence-transformers` (Model: `paraphrase-multilingual-MiniLM-L12-v2` for German support)
- **LLM Interface**: `ollama` (via HTTP API) or `openai` (for LM Studio compatibility)
- **Data Handling**: `pydantic` (Models), `numpy` (Vector ops)

## 4. Data Flow
1.  **Ingestion**: `Parser` -> `Document` -> `Chunker` -> `Chunks` -> `Embedding Service` -> `Vectors` -> `ChromaDB`.
2.  **Retrieval**: `User Query` -> `Embedding Service` -> `Query Vector` -> `ChromaDB` -> `Relevant Chunks`.
3.  **Generation**: `Relevant Chunks` + `User Query` + `System Prompt` -> `LLM` -> `Answer`.

## 5. Configuration (`config.yaml`)
The system must be configurable via the central configuration file:
```yaml
rag:
  chunk_size: 500
  chunk_overlap: 50
  embedding_model: "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
  top_k: 5
  similarity_threshold: 0.7
  persist_directory: "data/chromadb"
```

## 6. Dependencies
- **Phase 2 Parsers**: Requires stable `Document` objects as input.
- **Ollama/LM Studio**: Requires a running local LLM server.
- **Python 3.12+**: Environment.

## 7. Success Criteria
- [ ] **Ingestion**: Can ingest PDF/DOCX/XLSX files into ChromaDB.
- [ ] **Retrieval**: Returns relevant chunks for test queries (Recall > 0.8).
- [ ] **Generation**: LLM answers questions based *only* on provided context.
- [ ] **Performance**: Retrieval < 200ms, Full Chain < 5s (depending on LLM).
- [ ] **Privacy**: Zero external network calls during operation.
