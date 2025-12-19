# Frontend Analysis

## 1. Frontend Structure Analysis

### 1.1 Directory Structure
The frontend is located in `option_2_platform/frontend/` and follows a standard FastAPI + Jinja2 structure:

- **`main.py`**: Entry point for the frontend application.
- **`routers/`**: Contains route handlers (`dashboard.py`, `projects.py`).
- **`templates/`**: Jinja2 HTML templates.
- **`static/`**: Static assets (CSS/JS).
- **`requirements.txt`**: Dependencies (`fastapi`, `uvicorn`, `jinja2`, `python-multipart`, `httpx`).

### 1.2 Technology Stack
- **Backend Framework:** FastAPI (Python)
- **Templating:** Jinja2 (Server-Side Rendering)
- **Interactivity:** HTMX (Hypermedia-Driven) + Alpine.js (Lightweight Reactivity)
- **Styling:** Tailwind CSS (Utility-first)
- **Build System:** None required (Python-based serving).

### 1.3 Functional Analysis
- **Dashboard (`/`)**: Lists projects and simple statistics.
- **Projects (`/projects`)**:
    - Create Project (Form)
    - Project Detail View
    - Document Upload (HTMX-based)
    - Document List

### 1.4 Current Backend Access
- **Direct Imports:** The frontend currently attempts to import services directly from a `backend` package (`from backend.services.project_service import ...`).
- **Issue:** The actual backend code is located in `src/`, not `backend/`. This indicates broken imports or a legacy structure assumption.
- **No API:** There is currently no distinct REST API layer; the frontend routers call service classes directly.

---

## 2. Backend API Potential

The RAG system (`src/rag`) offers powerful capabilities that should be exposed via a REST API.

### 2.1 Available Backend Functions

| Domain | Function | Backend Class/Method |
|--------|----------|----------------------|
| **Ingestion** | Ingest Document | `IngestionPipeline.ingest_file()` |
| | Ingest Directory | `IngestionPipeline.ingest_directory()` |
| **Retrieval** | Semantic Search | `RetrievalEngine.retrieve()` |
| **LLM** | Ask Question | `LLMChain.query()` |
| | Check Status | `OllamaProvider.is_available()` |
| **System** | Get Config | `RAGConfig.from_yaml()` |

### 2.2 Proposed API Design

**Ingestion Endpoints**
- `POST /api/ingest/upload`: Upload and process a file.
- `GET /api/ingest/status/{job_id}`: Check processing status.

**Query Endpoints**
- `POST /api/query`: Execute a RAG query.
    - Body: `{ "question": "...", "template": "standard" }`
- `POST /api/query/stream`: Stream the response (optional).

**System Endpoints**
- `GET /api/system/status`: Check Ollama and ChromaDB status.
- `GET /api/system/config`: Retrieve current configuration.

---

## 3. Architecture Assessment

### 3.1 Current Architecture
- **Monolithic:** Frontend and Backend logic are tightly coupled via direct Python imports.
- **Broken Integration:** Frontend imports `backend.*` which does not exist (should be `src.*`).
- **Server-Side Rendering:** Heavy reliance on Jinja2 for UI state.

### 3.2 Evaluation against Principles

1.  **Backend-First:** ⚠️ **Partial.** The RAG backend (`src/rag`) is independent, but the frontend code tries to bypass the API layer.
2.  **API-Driven:** ❌ **No.** Frontend calls Python classes directly. No clear API contract.
3.  **Thin Frontend:** ✅ **Yes.** HTMX/Alpine keeps client-side logic minimal.
4.  **Debugging-Friendly:** ❌ **No.** Errors in service calls will likely crash the page render rather than showing a nice error message.
5.  **Error Isolation:** ❌ **No.** Tightly coupled.

---

## 4. Gap Analysis

### 4.1 Feature Gaps
- **Chat Interface:** The most critical missing feature. There is no UI to ask questions to the RAG system.
- **RAG Integration:** Document upload exists but likely doesn't trigger the `IngestionPipeline`.
- **Status Indicators:** No UI to show if Ollama is running or if Embeddings are being generated.
- **Citations:** No UI to display source citations returned by the LLM.

### 4.2 API Gaps
- **REST Layer:** A dedicated `src/api` module is missing.
- **Async Processing:** Ingestion can be slow; the frontend needs an async/background task mechanism (or simple loading state) to handle large files.

### 4.3 Technology Gaps
- **Import Mismatch:** `backend` vs `src` namespace issue must be resolved.
