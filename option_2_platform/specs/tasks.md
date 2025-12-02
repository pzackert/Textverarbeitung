# Implementation Tasks: IFB PROFI Option 2

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Phase 1: LLM Infrastructure (Backend-First)
- [x] **Ollama Setup Script**: Create `scripts/setup_ollama.sh` (and .bat) to check for Ollama installation and pull required models (e.g., `qwen2.5:7b`). <!-- id: 1 -->
- [x] **LLM Client Adapter**: Create `backend/adapters/llm_client.py`. Implement a generic client that connects to the local Ollama/LM Studio API (base URL configurable). <!-- id: 2 -->
- [x] **Connection Tests**: Create `tests/integration/test_llm_connection.py`. Verify `GET /api/tags` (list models) and `POST /api/generate` (simple prompt). <!-- id: 3 -->
- [x] **Hello World Test**: Create a script `scripts/test_llm_inference.py` that sends "Hello World" to the LLM and prints the response speed and token count. <!-- id: 4 -->
- [ ] **Token Limit Handling**: Implement a utility in `backend/core/token_utils.py` to estimate token counts and truncate input if necessary. Add tests. <!-- id: 5 -->

## Phase 2: Document Processing
- [x] **Parser Interface**: Define `BaseParser` abstract class in `backend/core/interfaces.py`. <!-- id: 6 -->
- [x] **PDF Parser**: Implement `backend/parsers/pdf_parser.py` using `pypdf` or `pdfplumber`. Return structured text with page numbers. <!-- id: 7 -->
- [x] **DOCX Parser**: Implement `backend/parsers/docx_parser.py` using `python-docx`. <!-- id: 8 -->
- [x] **XLSX Parser**: Implement `backend/parsers/xlsx_parser.py` using `openpyxl` or `pandas`. <!-- id: 9 -->
- [x] **Unified Parser Service**: Create `backend/services/document_service.py` that selects the correct parser based on file extension. <!-- id: 10 -->
- [x] **Parser Tests**: Create `tests/unit/test_parsers.py` with sample files for each format. <!-- id: 11 -->

## Phase 3: RAG System
- [ ] **ChromaDB Adapter**: Create `backend/adapters/vector_store.py`. Initialize ChromaDB client (persistent mode). <!-- id: 12 -->
- [ ] **Embedding Service**: Implement embedding generation using a local model (e.g., `nomic-embed-text` via Ollama or `sentence-transformers`). <!-- id: 13 -->
- [ ] **Ingestion Pipeline**: Create `backend/services/rag_service.py`. Implement `ingest_document(text, metadata)` to chunk text and store embeddings. <!-- id: 14 -->
- [ ] **Retrieval Logic**: Implement `query(query_text, n_results)` in `RagService`. <!-- id: 15 -->
- [ ] **RAG Tests**: Create `tests/integration/test_rag.py`. Ingest a dummy text and verify it can be retrieved via query. <!-- id: 16 -->

## Phase 4: Criteria Engine
- [ ] **Criteria Schema**: Define the JSON schema for criteria in `backend/core/models.py` (e.g., `Criterion`, `CheckResult`). <!-- id: 17 -->
- [ ] **Criteria Catalog**: Create `config/criteria_catalog.json` with the 6 IFB PROFI criteria and their descriptions/prompts. <!-- id: 18 -->
- [ ] **Evaluation Logic**: Create `backend/services/criteria_engine.py`. Implement `evaluate_criterion(text_context, criterion)` which constructs the LLM prompt. <!-- id: 19 -->
- [ ] **Engine Tests**: Create `tests/unit/test_criteria_engine.py`. Mock the LLM response to test the parsing of the evaluation result (JSON/Structured output). <!-- id: 20 -->

## Phase 5: Backend Services (FastAPI)
- [ ] **Project Service Refactor**: Update `backend/services/project_service.py` to integrate with `DocumentService` and `RagService`. <!-- id: 21 -->
- [ ] **Analysis Endpoints**: Create `POST /projects/{id}/analyze` in `backend/routers/analysis.py`. Triggers the RAG ingestion and Criteria evaluation. <!-- id: 22 -->
- [ ] **Results Endpoints**: Create `GET /projects/{id}/results` to fetch evaluation status. <!-- id: 23 -->
- [ ] **API Tests**: Create `tests/api/test_analysis_routes.py`. <!-- id: 24 -->

## Phase 6: Frontend Integration
- [ ] **Analysis UI**: Update `project_detail.html` to include an "Analyze" button and a results section. <!-- id: 25 -->
- [ ] **HTMX Polling**: Implement HTMX polling to check the status of the analysis (since it might take time). <!-- id: 26 -->
- [ ] **Result Visualization**: Create a template to display the criteria results (Green/Red badges, reasoning text). <!-- id: 27 -->

## Phase 2: Document Parser Implementation

### 2.1 PDF Parser
- [ ] Implement `PDFParser` class using `pymupdf`
- [ ] Extract text and metadata (pages, author, dates)
- [ ] Unit tests (Init, Valid, Invalid, Missing, Corrupted)
- [ ] Real file tests (A_Perfekter_Fall, B_Mangelhafter_Fall)

### 2.2 DOCX Parser
- [ ] Implement `DocxParser` class using `python-docx`
- [ ] Extract text from paragraphs and tables
- [ ] Extract metadata (paragraphs, tables, author)
- [ ] Unit tests (Init, Valid, Invalid, Missing, Corrupted)
- [ ] Real file tests (A_Perfekter_Fall, B_Mangelhafter_Fall)

### 2.3 XLSX Parser
- [ ] Implement `XlsxParser` class using `openpyxl`
- [ ] Extract rows as individual documents
- [ ] Extract metadata (sheet, row, headers)
- [ ] Unit tests (Init, Valid, Invalid, Missing, Corrupted)
- [ ] Real file tests (D_Test)

### 2.4 Real-World Testing
- [ ] Test all files in `option_1_mvp/data/input` subdirectories
- [ ] Generate test report
