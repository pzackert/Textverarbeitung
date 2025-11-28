# Project Constitution: IFB PROFI Option 2 (Platform)

## 1. Vision & Scope
**Goal:** Develop a production-ready, single-user platform for automated grant application review using local AI.
**Type:** "Lite" Architecture (Option 2).
**Key Constraint:** 100% Local Processing (Privacy First). No external API calls for inference.

## 2. Technical Stack
- **Language:** Python 3.10+
- **Package Manager:** `uv` (Strict requirement)
- **Backend Framework:** FastAPI
- **Frontend:** Server-Side Rendered (SSR) with Jinja2 + HTMX + TailwindCSS
- **LLM Engine:** Ollama or LM Studio (Local Inference Server)
- **Vector Database:** ChromaDB (Local persistence)
- **Storage:** Local Filesystem (JSON for metadata, folders for documents)
- **Testing:** `pytest` (Required for all backend components)

**Data Formats:**
- **TOON** (Token-Optimized Object Notation) - for criteria catalogs
  - 61% fewer tokens than JSON
  - Perfect for tabular data
  - LLM-optimized syntax
  - Use for: Criteria catalogs, evaluation results
- JSON - for general data interchange
- TOML - for configuration files

## 3. Development Principles

### A. Backend-First & Test-Driven
We strictly follow the implementation order:
1.  **Core Logic/Infrastructure** (LLM connection, Parsers)
2.  **Service Layer** (RAG, Criteria Engine)
3.  **API Layer** (FastAPI Routes)
4.  **UI Layer** (Templates/HTMX)

**Rule:** No UI code is written until the underlying service is tested and functional.

### B. Modular Architecture
The codebase must be structured to allow easy replacement of components (e.g., swapping the PDF parser or the Vector DB).
- `backend/core`: Domain models and interfaces.
- `backend/services`: Business logic implementation.
- `backend/adapters`: External system integrations (Ollama, ChromaDB).

### C. Spec-Driven Development
- All work starts with a Task ID from `specs/tasks.md`.
- No code is written without a corresponding specification in `specs/`.
- Documentation is updated *before* code changes.

### D. AI Interaction
- We use **Ollama** (or LM Studio) as the inference backend.
- We must handle context window limits explicitly.
- We must implement robust error handling for LLM timeouts or failures.

## 4. Directory Structure (Target)
```
option_2_platform/
├── backend/
│   ├── adapters/      # Ollama, ChromaDB clients
│   ├── core/          # Pydantic models, Interfaces
│   ├── parsers/       # PDF, DOCX, XLSX parsers
│   ├── services/      # RAG, Criteria, Project services
│   └── main.py        # FastAPI entry point
├── frontend/
│   ├── static/
│   ├── templates/
│   └── routers/
├── data/              # Local storage (gitignored)
├── specs/             # Spec Kit documentation
├── tests/             # Pytest suite
└── pyproject.toml     # Dependencies
```
