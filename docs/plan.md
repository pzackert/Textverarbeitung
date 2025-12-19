# Implementation Plan: IFB PROFI Option 2 (Platform)

**Spec**: [spec.md](./spec.md) | **Tasks**: [tasks.md](./tasks.md)

## Summary
This plan outlines the technical execution for the "Option 2: Platform" variant. The focus is on a robust, modular architecture that prioritizes local processing and privacy. We adhere to a "Backend-First" strategy, ensuring the AI and Data layers are solid before building the UI.

## Architecture Overview
- **Core**: Pydantic models for strict data validation.
- **Adapters**: Isolated clients for Ollama (LLM) and ChromaDB (Vector Store) to prevent vendor lock-in.
- **Services**: Business logic (Project Management, Document Parsing, RAG, Criteria Evaluation).
- **API**: FastAPI for RESTful endpoints.
- **UI**: Server-Side Rendering with Jinja2 and HTMX for a responsive but simple frontend.

## Phase Breakdown

### Phase 1: LLM Infrastructure
**Goal**: Establish a reliable connection to the local Inference Server (Ollama).
**Key Tech**: `httpx` (async HTTP client), `ollama` (CLI/Server).
**Validation**: Automated tests must prove we can send a prompt and get a response within acceptable timeframes.

### Phase 2: Document Processing
**Goal**: Convert raw user uploads (PDF, DOCX, XLSX) into clean, chunkable text.
**Key Tech**: `pypdf`, `python-docx`, `openpyxl`.
**Strategy**: Implement a Factory Pattern (`DocumentService`) to delegate to specific parsers.

### Phase 3: RAG System
**Goal**: Enable semantic search over project documents.
**Key Tech**: `chromadb` (Local persistence).
**Flow**: Parse -> Chunk -> Embed -> Store -> Retrieve.
**Note**: We will use a local embedding model (e.g., `nomic-embed-text`) to ensure 100% offline capability.

### Phase 4: Criteria Engine
**Goal**: Automate the decision-making process based on the retrieved context.
**Key Tech**: Prompt Engineering, JSON Mode (if supported by model) or strict output parsing.
**Data**: The criteria are defined in `config/criteria_catalog.json` to allow easy updates without code changes.

### Phase 5: Backend Services
**Goal**: Expose the core logic via a REST API.
**Key Tech**: `FastAPI`, `BackgroundTasks` (for long-running analysis).
**Endpoints**:
- `POST /analyze`: Starts the async analysis pipeline.
- `GET /results`: Polling endpoint for UI.

### Phase 6: Frontend Integration
**Goal**: Provide a user-friendly interface for the complex backend logic.
**Key Tech**: `HTMX` (for async interactions without complex JS), `TailwindCSS`.
**UX**: Users upload docs -> Click Analyze -> See progress bar -> View detailed results.

## Risk Management
- **LLM Hallucinations**: Mitigated by RAG (grounding) and explicit "Reasoning" output requirements.
- **Performance**: Local inference can be slow. We will use async queues/background tasks and HTMX polling to keep the UI responsive.
- **Context Limits**: We will implement strict token counting and chunking strategies.
