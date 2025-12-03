# Test Strategy (Phase 3)

## 1. Unit Tests (`tests/test_rag/`)
Isolated tests for individual components.

### 1.1 Chunker Tests
- `test_chunk_size`: Verify chunks do not exceed max size.
- `test_chunk_overlap`: Verify overlap exists between sequential chunks.
- `test_metadata_preservation`: Ensure chunks carry over parent doc metadata.

### 1.2 Vector Store Tests
- `test_add_documents`: Add dummy docs and verify count.
- `test_query_similarity`: Add known vectors and query for them.
- `test_persistence`: Verify data remains after client restart.

### 1.3 LLM Client Tests
- `test_ollama_connection`: Ping Ollama server.
- `test_generate_response`: Send simple prompt, check response format.
- `test_error_handling`: Simulate timeout/connection error.

## 2. Integration Tests
End-to-End pipeline tests.

- `test_ingestion_pipeline`: Parser -> Chunker -> Vector Store.
- `test_retrieval_pipeline`: Query -> Vector Store -> Result Chunks.
- `test_full_rag_chain`: Query -> Retrieval -> LLM -> Answer.

## 3. Test Data
- **Synthetic Data**: Simple text files for unit tests.
- **Real Data**: The 12 files from Phase 2 (`option_1_mvp/data/input/`) for integration tests.

## 4. Performance Tests
- **Ingestion Speed**: Measure time to ingest 10 documents.
- **Retrieval Latency**: Measure time for 100 queries.
- **Target**: Retrieval < 200ms.

## 5. Quality Metrics
- **Recall@5**: Is the correct chunk in the top 5 results? (Manual verification for a set of 10 queries).
- **Answer Relevance**: Does the LLM answer match the ground truth? (Manual review).

## 6. Coverage Target
- Minimum **80%** code coverage for `src/rag/`.
