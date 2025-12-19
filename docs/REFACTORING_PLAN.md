# Refactoring Plan: RAG Backend Integration

## Overview
This plan outlines the steps to integrate the newly developed RAG backend (`src/rag`) into the existing frontend (`option_2_platform/frontend`). The goal is to transition from a broken, direct-import architecture to a clean, API-driven design.

## Phase 1: API Layer Implementation (Backend)

**Objective:** Expose RAG capabilities via standard REST endpoints.

### 1.1 Create API Structure
- **Location:** `src/api/`
- **Files:**
    - `__init__.py`
    - `main.py`: FastAPI application factory.
    - `dependencies.py`: Dependency injection (RAG components).
    - `routers/ingest.py`: Document processing endpoints.
    - `routers/query.py`: LLM interaction endpoints.
    - `routers/system.py`: Health checks and config.
    - `schemas.py`: Pydantic models for API contracts.

### 1.2 Implement Endpoints
- **`POST /api/v1/ingest/upload`**: Accepts file upload, saves to `data/input`, triggers `IngestionPipeline`.
- **`POST /api/v1/query`**: Accepts JSON `{ "query": "..." }`, calls `LLMChain`, returns answer + sources.
- **`GET /api/v1/system/health`**: Checks connection to Ollama and Vector DB.

---

## Phase 2: Frontend Adaptation

**Objective:** Decouple frontend from backend logic and add missing UI features.

### 2.1 Fix Namespace & Imports
- **Action:** Remove all `from backend.services...` imports in `frontend/routers/`.
- **Replacement:** Create a `frontend/services/api_client.py` (or similar) that interacts with the RAG system.
    - *Note:* Since this is a monolithic FastAPI app, we can import `src` directly, but we should do it via a clean "Service Layer" interface, not raw class instantiation in routers.

### 2.2 Implement Chat Interface
- **New Page:** `frontend/templates/chat.html`
- **New Route:** `frontend/routers/chat.py` (`GET /chat`)
- **Features:**
    - Chat history display.
    - Input field with HTMX (`hx-post="/api/v1/query"`).
    - Markdown rendering for LLM responses.
    - Source citation display.

### 2.3 Connect Document Upload
- **Update:** `frontend/routers/projects.py`
- **Logic:**
    1. Save uploaded file to disk.
    2. **NEW:** Call `IngestionPipeline.ingest_file()` immediately (or enqueue background task).
    3. **NEW:** Provide feedback to UI (Success/Error/Processing).

---

## Phase 3: Integration & Cleanup

### 3.1 Unified Application Entry Point
- **Create:** `src/main.py` (Root application).
- **Logic:**
    - Mounts API Router at `/api/v1`.
    - Mounts Frontend Router at `/`.
    - Mounts Static Files.
- **Deprecate:** `option_2_platform/frontend/main.py` (merge into `src/main.py`).

### 3.2 Testing
- **Unit Tests:** Test API endpoints in isolation.
- **E2E Tests:** Test the full flow: Upload File -> Ingest -> Ask Question -> Verify Answer.

---

## Execution Steps

1.  **Create `src/api` module** and implement basic Health Check.
2.  **Implement `src/api/routers/query.py`** wrapping `LLMChain`.
3.  **Implement `src/api/routers/ingest.py`** wrapping `IngestionPipeline`.
4.  **Create `src/main.py`** to serve both API and Frontend.
5.  **Refactor Frontend Routers** to use `src` services correctly.
6.  **Build Chat UI** (HTML/CSS/JS).
