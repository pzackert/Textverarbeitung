# Test Strategy (Phase 3)

## 1. Unit Tests (`tests/test_rag/`)
Isolierte Tests für einzelne Komponenten.

### 1.1 Chunker Tests
- `test_chunk_size`: Verifiziert, dass Chunks Max-Size nicht überschreiten.
- `test_chunk_overlap`: Verifiziert Überlappung.
- `test_metadata_preservation`: Prüft Metadaten-Vererbung.
- `test_german_splitting`: Prüft Splitting bei deutschen Umlauten/Sonderzeichen.

### 1.2 Vector Store Tests
- `test_add_documents`: Dummy-Docs hinzufügen und Count prüfen.
- `test_query_similarity`: Bekannte Vektoren suchen.
- `test_persistence`: Daten nach Client-Neustart noch da?

### 1.3 LLM Client Tests
- `test_ollama_connection`: Ping an Server.
- `test_generate_response`: Einfacher Prompt, Format-Check.
- `test_error_handling`: Timeout/Connection Error Simulation.

## 2. Integration Tests
End-to-End Pipeline Tests.

- `test_ingestion_pipeline`: Parser -> Chunker -> Vector Store.
- `test_retrieval_pipeline`: Query -> Vector Store -> Result Chunks.
- `test_full_rag_chain`: Query -> Retrieval -> LLM -> Antwort.

## 3. Test Daten
- **Synthetisch**: Einfache Textfiles für Unit Tests.
- **Real World**: Die 12 Dateien aus Phase 2 (`option_1_mvp/data/input/`) für Integration Tests.

## 4. Performance Tests
- **Ingestion Speed**: Zeit für 10 Dokumente messen.
- **Retrieval Latency**: Zeit für 100 Queries messen.
- **Target**: Retrieval < 200ms.

## 5. Quality Metrics
- **Recall@5**: Ist der korrekte Chunk in den Top 5? (Manuelle Verifikation).
- **Answer Relevance**: Passt die Antwort zur Ground Truth?

## 6. Coverage Target
- Minimum **80%** Code Coverage für `src/rag/`.

