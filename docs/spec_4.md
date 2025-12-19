# RAG System - Specification

## Goal
Implement a local Retrieval-Augmented Generation (RAG) system using ChromaDB to provide semantic context for LLM queries, ensuring data privacy and high relevance.

## Requirements

### Functional
- [ ] **Ingestion Pipeline**:
  - Accept `ParsedDocument` objects (from Phase 2).
  - Split text into semantic chunks (overlapping windows).
  - Generate embeddings using a local model.
  - Store chunks + metadata in ChromaDB.
- [ ] **Retrieval**:
  - Semantic search by query text.
  - Filter by `project_id` or `document_type`.
  - Return top-k results with relevance scores.
- [ ] **Context Management**:
  - Assemble context window respecting token limits (e.g., 4096 tokens).
  - Prioritize most relevant chunks.
- [ ] **Persistence**: Data must persist across server restarts (local disk storage).

### Non-Functional
- [ ] **Local-First**: No external embedding APIs (use `nomic-embed-text` or `all-MiniLM-L6-v2`).
- [ ] **Performance**: Retrieval latency < 200ms for a database of 1000 chunks.
- [ ] **Privacy**: All vector data stored locally in `data/chromadb/`.
- [ ] **Scalability**: Support up to 100 projects (approx. 10,000 chunks).

## Input/Output Definitions

### Embedding Model
- **Model**: `nomic-embed-text-v1.5` (via Ollama) or `sentence-transformers/all-MiniLM-L6-v2` (via Python).
- **Dimension**: 768 (nomic) or 384 (MiniLM).

### Ingestion Interface (`src/rag/ingestion.py`)
```python
class RagIngestor:
    async def ingest(self, document: ParsedDocument, project_id: str) -> int:
        """
        Chunks, embeds, and stores the document.
        Returns the number of chunks created.
        """
        ...
```

### Retrieval Interface (`src/rag/retrieval.py`)
```python
class RagRetriever:
    async def query(
        self, 
        query_text: str, 
        project_id: str, 
        top_k: int = 5
    ) -> List[RagChunk]:
        """Retrieves relevant chunks for a project."""
        ...

class RagChunk(BaseModel):
    chunk_id: str
    text: str
    score: float
    metadata: Dict[str, Any] # page, filename, etc.
```

## Test Cases

| ID | Name | Description | Expected Result |
|----|------|-------------|-----------------|
| TC-RAG-01 | **Ingestion** | Ingest a sample PDF content | Chunks stored in ChromaDB, count > 0 |
| TC-RAG-02 | **Embedding** | Generate embedding for "Hello" | Returns vector of correct dimension |
| TC-RAG-03 | **Retrieval** | Query "Finanzplan" | Returns chunks containing financial data |
| TC-RAG-04 | **Project Filter** | Query Project A for Project B data | Returns 0 results (strict isolation) |
| TC-RAG-05 | **Persistence** | Restart service, query again | Data still available |
| TC-RAG-06 | **Token Limit** | Build context > 4k tokens | Truncates/selects chunks to fit limit |

## Success Criteria
- [ ] Retrieval speed < 200ms.
- [ ] Top-3 results contain the correct answer for known queries.
- [ ] Data isolation between projects is verified.
- [ ] No external API calls for embeddings.

## Dependencies
- `chromadb` (Vector Database)
- `sentence-transformers` (or `ollama` for embeddings)
- `langchain-text-splitters` (RecursiveCharacterTextSplitter)
- `numpy` (Vector operations)

## Files to Create
- `src/rag/client.py` (ChromaDB wrapper)
- `src/rag/embeddings.py`
- `src/rag/ingestion.py`
- `src/rag/retrieval.py`
- `src/rag/utils.py` (Chunking logic)
- `tests/test_rag/test_ingestion.py`
- `tests/test_rag/test_retrieval.py`
