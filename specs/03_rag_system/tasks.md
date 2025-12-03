# Implementation Tasks (Phase 3)

## 1. Foundation & Setup
- [ ] **Task 3.1.1**: Create `src/rag/` directory structure (`__init__.py`, `models.py`, `exceptions.py`).
- [ ] **Task 3.1.2**: Define `Chunk` data model in `src/rag/models.py`.
- [ ] **Task 3.1.3**: Implement `RAGException` classes in `src/rag/exceptions.py`.

## 2. Chunking Engine
- [ ] **Task 3.2.1**: Implement `Chunker` class in `src/rag/chunker.py`.
- [ ] **Task 3.2.2**: Add recursive character splitting logic.
- [ ] **Task 3.2.3**: Add unit tests for Chunker (`tests/test_rag/test_chunker.py`).

## 3. Vector Store (ChromaDB)
- [ ] **Task 3.3.1**: Implement `VectorStore` class in `src/rag/vector_store.py`.
- [ ] **Task 3.3.2**: Implement `initialize_collection` method.
- [ ] **Task 3.3.3**: Implement `add_documents` method.
- [ ] **Task 3.3.4**: Implement `query` method.
- [ ] **Task 3.3.5**: Add unit tests for VectorStore (`tests/test_rag/test_vector_store.py`).

## 4. Embedding Service
- [ ] **Task 3.4.1**: Implement `EmbeddingService` in `src/rag/embeddings.py`.
- [ ] **Task 3.4.2**: Integrate `sentence-transformers`.
- [ ] **Task 3.4.3**: Add caching mechanism (optional but recommended).

## 5. Retrieval Engine
- [ ] **Task 3.5.1**: Implement `Retriever` class in `src/rag/retriever.py`.
- [ ] **Task 3.5.2**: Implement `retrieve(query, top_k)` logic.
- [ ] **Task 3.5.3**: Implement metadata filtering logic.
- [ ] **Task 3.5.4**: Add unit tests for Retriever.

## 6. LLM Integration
- [ ] **Task 3.6.1**: Update `src/ollama/client.py` to support RAG prompts.
- [ ] **Task 3.6.2**: Create `PromptTemplate` class in `src/rag/prompts.py`.
- [ ] **Task 3.6.3**: Implement `generate_rag_response(query, context)` method.

## 7. RAG Pipeline (Orchestration)
- [ ] **Task 3.7.1**: Implement `RAGPipeline` class in `src/rag/pipeline.py`.
- [ ] **Task 3.7.2**: Connect Parser -> Chunker -> Vector Store (Ingestion).
- [ ] **Task 3.7.3**: Connect Query -> Retriever -> LLM (Inference).
- [ ] **Task 3.7.4**: Create CLI/Script for testing the full pipeline.

## 8. Documentation & Validation
- [ ] **Task 3.8.1**: Run full integration tests with real IFB documents.
- [ ] **Task 3.8.2**: Create `docs/13_RAG_USAGE.md`.
- [ ] **Task 3.8.3**: Update `PROJECT_STATUS.md`.
