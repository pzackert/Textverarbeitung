# Implementation Tasks (Phase 3)

## 1. Foundation (Tasks 1-5)
- [ ] **Task 1**: Erstelle Verzeichnisstruktur `src/rag/` (`__init__.py`, `models.py`, `exceptions.py`).
- [ ] **Task 2**: Definiere `Chunk` Data Model in `src/rag/models.py`.
- [ ] **Task 3**: Implementiere `RAGException` Klassen in `src/rag/exceptions.py`.
- [ ] **Task 4**: Erstelle `src/rag/config.py` für RAG-spezifische Konfiguration.
- [ ] **Task 5**: Aktualisiere `config/config.yaml` mit RAG-Parametern.

## 2. Chunking (Tasks 6-10)
- [ ] **Task 6**: Erstelle `src/rag/chunker.py` und `Chunker` Klasse.
- [ ] **Task 7**: Implementiere Recursive Character Splitting Logik.
- [ ] **Task 8**: Implementiere Metadaten-Vererbung (Document -> Chunk).
- [ ] **Task 9**: Implementiere Unit Tests für Chunker (`tests/test_rag/test_chunker.py`).
- [ ] **Task 10**: Validiere Chunking mit deutschen Beispieltexten.

## 3. Embeddings (Tasks 11-15)
- [ ] **Task 11**: Erstelle `src/rag/embeddings.py` und `EmbeddingService` Klasse.
- [ ] **Task 12**: Integriere `sentence-transformers` Library.
- [ ] **Task 13**: Implementiere `get_embedding(text)` Methode.
- [ ] **Task 14**: Implementiere Caching (Optional/Basic).
- [ ] **Task 15**: Unit Tests für Embedding Service (`tests/test_rag/test_embeddings.py`).

## 4. Vector Store (Tasks 16-25)
- [ ] **Task 16**: Erstelle `src/rag/vector_store.py` und `VectorStore` Klasse.
- [ ] **Task 17**: Implementiere ChromaDB Client Initialisierung.
- [ ] **Task 18**: Implementiere `get_or_create_collection`.
- [ ] **Task 19**: Implementiere `add_documents(chunks)` Methode.
- [ ] **Task 20**: Implementiere Metadaten-Mapping für ChromaDB.
- [ ] **Task 21**: Implementiere `query(text, top_k)` Methode.
- [ ] **Task 22**: Implementiere `delete(source)` Methode.
- [ ] **Task 23**: Implementiere `persist()` (falls nötig, ChromaDB macht das oft auto).
- [ ] **Task 24**: Unit Tests für Vector Store (`tests/test_rag/test_vector_store.py`).
- [ ] **Task 25**: Integrationstest: Add -> Query -> Verify.

## 5. Retrieval (Tasks 26-35)
- [ ] **Task 26**: Erstelle `src/rag/retriever.py` und `Retriever` Klasse.
- [ ] **Task 27**: Implementiere `retrieve(query)` Hauptmethode.
- [ ] **Task 28**: Implementiere Query Preprocessing (Cleaning).
- [ ] **Task 29**: Implementiere Metadaten-Filterung Logik.
- [ ] **Task 30**: Implementiere Threshold-Filterung.
- [ ] **Task 31**: Implementiere Result-Ranking/Sorting.
- [ ] **Task 32**: Implementiere Context Assembly (Chunks zu String).
- [ ] **Task 33**: Implementiere Token-Limit Truncation.
- [ ] **Task 34**: Unit Tests für Retriever (`tests/test_rag/test_retriever.py`).
- [ ] **Task 35**: Integrationstest: Query -> Context String.

## 6. LLM Chain (Tasks 36-45)
- [ ] **Task 36**: Erstelle `src/rag/chain.py` und `RAGChain` Klasse.
- [ ] **Task 37**: Definiere Prompt Templates in `src/rag/prompts.py`.
- [ ] **Task 38**: Implementiere `generate_answer(query, context)` Methode.
- [ ] **Task 39**: Integriere `src.ollama.OllamaClient`.
- [ ] **Task 40**: Implementiere Error Handling (Retries).
- [ ] **Task 41**: Implementiere Response Parsing.
- [ ] **Task 42**: Implementiere "Keine Info gefunden" Fallback.
- [ ] **Task 43**: Unit Tests für RAG Chain (`tests/test_rag/test_chain.py`).
- [ ] **Task 44**: Mock-Tests für LLM Calls.
- [ ] **Task 45**: Integrationstest mit echtem Ollama Server.

## 7. Testing & Validation (Tasks 46-60)
- [ ] **Task 46**: Erstelle `scripts/test_ingestion.py` (Batch Ingestion).
- [ ] **Task 47**: Führe Ingestion für alle 12 Real-World Files durch.
- [ ] **Task 48**: Erstelle `scripts/test_retrieval.py` (Query Testing).
- [ ] **Task 49**: Definiere 10 Test-Fragen für die Real-World Docs.
- [ ] **Task 50**: Führe Retrieval-Tests durch und messe Recall.
- [ ] **Task 51**: Erstelle `scripts/test_full_chain.py`.
- [ ] **Task 52**: Führe End-to-End Tests durch (Frage -> Antwort).
- [ ] **Task 53**: Validiere Antworten manuell auf Korrektheit.
- [ ] **Task 54**: Performance Check: Ingestion Zeit.
- [ ] **Task 55**: Performance Check: Retrieval Zeit.
- [ ] **Task 56**: Performance Check: Generation Zeit.
- [ ] **Task 57**: Prüfe Memory Usage während Ingestion.
- [ ] **Task 58**: Prüfe Disk Space Usage von ChromaDB.
- [ ] **Task 59**: Fixe gefundene Bugs/Issues.
- [ ] **Task 60**: Finaler Run aller Tests (`uv run pytest`).

## 8. Documentation (Tasks 61-65)
- [ ] **Task 61**: Erstelle `docs/13_RAG_USAGE.md`.
- [ ] **Task 62**: Dokumentiere Konfigurations-Optionen.
- [ ] **Task 63**: Dokumentiere API/Interface Nutzung.
- [ ] **Task 64**: Update `PROJECT_STATUS.md` (Phase 3 Complete).
- [ ] **Task 65**: Merge `feature/rag-system` in `main`.
