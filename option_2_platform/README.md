# IFB PROFI Platform (Local RAG)

A local-first AI platform for validating funding applications ("Anträge") against a criteria catalog using RAG (Retrieval Augmented Generation).

## 🚀 Quick Start

```bash
# 1. Setup
git clone <repo>
cd option_2_platform
uv sync

# 2. Run
uv run uvicorn src.api.main:app --reload
```
Open [http://localhost:8000](http://localhost:8000).

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

| Guide | Description |
| :--- | :--- |
| **[01. Installation](docs/01_INSTALLATION_SETUP.md)** | Requirements, dependencies, and LLM setup (Ollama/LM Studio). |
| **[02. Startup Lifecycle](docs/02_STARTUP_LIFECYCLE.md)** | System initialization, auto-healing, and shutdown logic. |
| **[03. Data Architecture](docs/03_DATA_ARCHITECTURE.md)** | Directory structure, data isolation, and persistence. |
| **[04. Backend API](docs/04_BACKEND_API.md)** | Endpoint reference for Projects, RAG, Queue, and Settings. |
| **[05. Frontend Guide](docs/05_FRONTEND_GUIDE.md)** | Architecture, state management, and UI logic (Jinja2 + Alpine). |
| **[06. Testing](docs/06_TESTING_STRATEGY.md)** | Automated test suite and manual validation steps. |

## Key Features

- **Local-First**: All data stays on your machine (`data/input`).
- **RAG Engine**: Vector search with ChromaDB and dynamic source citation.
- **Criteria Validation**: Automated checking of documents against regulatory criteria.
- **Self-Healing**: Robust startup sequence repairs missing configurations/folders.

## License
Proprietary / Internal Use Only.
