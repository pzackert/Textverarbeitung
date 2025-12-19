# API & System Architecture Analysis

## 1. Status Quo vs. Specification
You have proposed a strict separation with a RESTful API, but the current implementation is a **Hybrid Monolith**.

### Current State (What I found):
- **Backend API (`src/api/`)**: Exists! Implements `/query`, `/ingest`, `/system`.
    - ⚠️ **Missing:** `GET /rag/documents` (List), `DELETE /rag/documents` (Delete), `POST /chat/direct` (Direct Chat).
    - ⚠️ **Startup:** No explicit `POST /startup` endpoint. Initialization happens implicitly or via `GET /health`.
- **Frontend (`frontend/`)**: **Bypasses the API**.
    - It imports `src.services.project_service` directly.
    - It runs in the same Python process as the backend services.

### The Gap:
To achieve your goal ("Backend und Frontend kommunizieren über API"), we must:
1.  **Refactor Frontend**: Replace `project_service.create_project(...)` with `await http_client.post("/api/projects", ...)` calls.
2.  **Complete Backend**: Implement the missing CRUD endpoints for Documents and Projects.

---

## 2. Startup Orchestration Analysis
Your plan for a "System Startup" flow is **excellent and necessary** for a local AI app, as loading models (Ollama/Embeddings) takes time.

**Proposed vs. Reality:**
- **Proposed**: `POST /api/system/startup` triggers checks; Middleware blocks traffic until ready.
- **Current**: `GET /system/health` checks status on-demand.

**Recommendation:**
- Implement the `POST /api/system/startup` endpoint.
- Use a global `SystemState` (Singleton) to track status (`INITIALIZING`, `READY`, `ERROR`).
- Middleware should return `503 Service Unavailable` with `Retry-After` if state != `READY`.

---

## 3. Analysis of Specific Endpoints

### 3.1 Health & Init
- **Spec**: `GET /health`, `POST /startup`, `GET /status`.
- **Current**: `GET /system/health` (Combined check).
- **Verdict**: **Approved.** Split `/health` (Kubernetes/Docker style, fast) from `/status` (App logic, detailed).

### 3.2 RAG Document Management
- **Spec**: Ingest, List, Get, Delete, Clear.
- **Current**: Only `POST /ingest/upload`.
- **Verdict**: **Critical Gap.** You cannot build the "Documents" tab in the UI without `GET /documents` and `DELETE`.
- **Action**: Implement `src/api/routers/documents.py`.

### 3.3 Chat
- **Spec**: `POST /chat/direct` (Raw LLM) and `POST /rag/query` (RAG).
- **Current**: Only `POST /query` (RAG).
- **Verdict**: **Gap.** Sometimes users just want to talk to the model without RAG context. Add `/chat/direct`.

---

## 4. Risks & Challenges

### 4.1 "Blocking" Calls
- The current `ingest_file` implementation is blocking (synchronous).
- **Risk**: Uploading a 50MB PDF will freeze the API server for 30+ seconds.
- **Solution**: Use `BackgroundTasks` (FastAPI native) or a queue. Your spec mentions "Timeouts: 30-120s" - this is too long for a web request. Use polling:
    1. `POST /ingest` -> Returns `task_id` (202 Accepted).
    2. `GET /tasks/{task_id}` -> Returns status ("processing", "done").

### 4.2 Shared Process vs. Separate Service
- IF you run `uv run uvicorn frontend.main:app` (Monolith), the API and Frontend share memory.
- IF you want true separation, you should be able to run `uvicorn src.api.main:app` (Backend) and a separate Frontend process.
- **Decision**: For a local Python app, the Monolith approach (one process, internal API calls or direct calls) is simpler and uses less RAM. **However**, sticking to a strict API contract internally (even if calling logic directly) makes the code much cleaner.

---

## 5. Implementation Roadmap (Next Steps)

1.  **Backend Completion (High Priority)**:
    - Add `documents.py` router (List/Delete).
    - Add `chat.py` router (Direct Chat).
    - Add `startup` endpoint logic in `system.py`.

2.  **Frontend Refactor (Medium Priority)**:
    - Create `frontend/services/api_client.py` (which uses `httpx`).
    - Replace usage of `src.services.*` with `api_client.*`.

3.  **Verification**:
    - Start System.
    - Run `curl` command to `POST /startup`.
    - Verify Status `ready`.
    - Upload file via API.
    - Listings update.
