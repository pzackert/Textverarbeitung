# Option 2: Professional AI Platform

Local AI-powered grant application review platform with privacy-first architecture.

## 🎯 Project Status

**Current Phase:** Phase 4 Complete ✅  
**Next Phase:** Phase 5 - Criteria Engine

### Implemented Features
- ✅ Project Structure (Spec Kit compliant)
- ✅ Ollama Integration (qwen2.5:7b)
- ✅ Configuration System (config.yaml)
- ✅ Test Framework (PyTest)
- ✅ Document Parsing (PDF, DOCX, XLSX)
- ✅ RAG System (ChromaDB, Embeddings, Retrieval)
- ✅ LLM Chain (Prompting, Generation, Citations)

### In Development
- ⏳ Criteria Engine (Phase 5)
- ⏳ API Layer (Phase 6)
- ⏳ UI Integration (Phase 7)

## 🚀 Quick Start

For detailed installation instructions, please refer to the platform-specific guides:

- **macOS:** [Installation Guide](../docs/INSTALLATION_MAC.md)
- **Windows:** [Installation Guide](../docs/INSTALLATION_WINDOWS.md)
- **Deployment:** [Deployment Guide](../docs/18_deployment_guide.md)


### Prerequisites (must be running before start)
- **LM Studio** installed and running on `http://localhost:1234` (default in `config/config.yaml` uses LM Studio).
- **Ollama** installed and running on `http://localhost:11434` (fallback provider, also used for qwen2.5:7b pulls).
- Pull at least one model that matches `config/config.yaml` (default: `openai/gpt-oss-20b` for LM Studio, `qwen2.5:7b` for Ollama fallback).

### Quick Command (macOS/Linux)
```bash
# 1. Install uv (if not installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Setup Project (Run once)
cd option_2_platform
uv venv && uv sync

# 3. Start Application (ensure LM Studio or Ollama is running)
# Default port is 8000. You can change it with --port <NUMBER>
uv run uvicorn src.api.main:app --reload --port 8000
# From repo root, equivalently:
# uv --directory option_2_platform run uvicorn src.api.main:app --reload --port 8000
```

### Setup LLM Model (Required!)

**Before starting the frontend**, you must have a compatible LLM model:

**Option A: Install the default model (qwen2.5:7b)**
```bash
ollama serve  # Start Ollama in a separate terminal
ollama pull qwen2.5:7b
```

**Option B: Use an existing model**
Edit `config/config.yaml` to configure your provider (Ollama or LM Studio).

### Start Frontend

**Prerequisites:**
1. **LM Studio or Ollama must be running**
2. **Model configured in `config/config.yaml` and pulled locally**

Start the web interface:
```bash
uv run uvicorn src.api.main:app --reload --port 8000
```

Open [http://localhost:8000](http://localhost:8000) in your browser.

**Expected Startup:**
- The page will show the **3D Startup Screen** (Apple-Style Cover Flow)
- Components initialize sequentially (LM Studio/Ollama, Vector DB, RAG)
- If all components are ready (✓), you'll be automatically redirected to the dashboard
- If "LLM Modell" fails, the system will attempt to fallback to Ollama automatically

### RAG Demo
To test the complete RAG system (requires Ollama):
```bash
uv run python examples/rag_demo.py
```

### Documentation
- [User Guide](../docs/19_user_guide.md)
- [Deployment Guide](../docs/18_deployment_guide.md)
- [Performance Report](../docs/17_performance_report.md)










## 🏗️ Architecture

### Tech Stack
- **Backend:** FastAPI, Pydantic, Dependency Injection
- **Frontend:** Jinja2 Templates, HTMX, TailwindCSS
- **LLM:** Ollama (qwen2.5:7b, qwen2.5:0.5b) or LM Studio
- **Vector DB:** ChromaDB (local persistence)
- **Storage:** Local filesystem (JSON metadata, document folders)
- **Testing:** PyTest

### Project Structure (Spec Kit Compliant)

```
option_2_platform/
├── src/                    # Source code (Backend-First)
│   ├── ollama/            # LLM client integration
│   ├── parsers/           # Document parsing (Phase 2)
│   ├── rag/               # RAG system (Phase 3)
│   ├── criteria/          # Criteria engine (Phase 4)
│   ├── services/          # Business logic
│   └── core/              # Shared models & config
├── tests/                 # Test suite (PyTest)
│   ├── test_ollama/       # LLM integration tests
│   ├── test_parsers/      # Parser tests
│   ├── test_rag/          # RAG tests
│   └── test_criteria/     # Criteria tests
├── config/                # Configuration files
│   ├── ollama.toml        # LLM configuration
│   └── criteria/          # Criteria catalogs
├── specs/                 # Specification documents
│   ├── constitution.md    # Project principles
│   ├── plan.md           # Implementation plan
│   └── tasks.md          # Task breakdown
├── docs/                  # Documentation
├── data/                  # Local data storage (gitignored)
├── logs/                  # Application logs
├── pyproject.toml         # Project dependencies
└── README.md             # This file
```

---

## 🔧 Configuration

### Switching Models

Edit `config/ollama.toml`:

```toml
[ollama]
provider = "ollama"
base_url = "http://localhost:11434"
default_model = "qwen2.5:7b"  # Change to "qwen2.5:0.5b" for faster inference
timeout = 30
```

### Using LM Studio Instead

```toml
[ollama]
provider = "lmstudio"
base_url = "http://localhost:1234/v1"
default_model = "qwen/qwen3-4b-thinking-2507"
timeout = 30
```

### Token Configuration

```toml
[generation]
max_tokens = 2048        # Maximum tokens to generate
n_ctx = 4096            # Context window size
temperature = 0.7       # Randomness (0.0 = deterministic, 1.0 = creative)
```

**Recommendations:**
- **qwen2.5:7b:** Better quality, use for production
- **qwen2.5:0.5b:** 2.5x faster, use for development/testing
- **Context window:** 4096 tokens for most tasks, up to 32768 for qwen2.5:7b

---

## 🧪 Testing

### Run All Tests

```bash
uv run pytest tests/ -v
```

### Run Specific Phase

```bash
uv run pytest tests/test_ollama/ -v      # LLM integration
uv run pytest tests/test_parsers/ -v     # Document parsing
uv run pytest tests/test_rag/ -v         # RAG system
uv run pytest tests/test_criteria/ -v    # Criteria engine
```

### Manual LLM Connection Test

```bash
uv run python -c "
from src.ollama.client import OllamaClient
client = OllamaClient()
response = client.generate('Say hello in one word', max_tokens=5)
print(f'Response: {response}')
"
```

### Test Model Switching

```bash
uv run python -c "
from src.ollama.client import OllamaClient
import time

client = OllamaClient()
print('Testing qwen2.5:7b...')
start = time.time()
response1 = client.generate('Hello', max_tokens=5)
print(f'7b: {response1} ({time.time()-start:.2f}s)')

client.model_name = 'qwen2.5:0.5b'
print('Testing qwen2.5:0.5b...')
start = time.time()
response2 = client.generate('Hello', max_tokens=5)
print(f'0.5b: {response2} ({time.time()-start:.2f}s)')
"
```

---

## 📊 Performance Metrics

### Tested on Apple M1 Pro

| Model | Avg Response Time | Throughput | VRAM Usage |
|-------|------------------|------------|------------|
| qwen2.5:7b | 0.47s | ~84 req/min | 4.6 GiB |
| qwen2.5:0.5b | 0.19s | ~200 req/min | 0.5 GiB |

**Note:** First request has ~2.5s warmup time (model loading).

---

## 📚 Documentation

- **[Project Constitution](specs/constitution.md):** Core principles & guidelines
- **[Implementation Plan](specs/plan.md):** Phase-by-phase breakdown
- **[Task List](specs/tasks.md):** Detailed task tracking
- **[Testing Guide](docs/02_testing_guide.md):** How to test each component
- **[LLM Integration Report](logs/llm_integration_test_summary.txt):** Test results

---

## 🌿 Git Workflow

### Branches

- `main` - Stable, production-ready code
- `cleanup/project-structure` - Cleanup branch (merged)
- `feature/document-parser` - Current development (Phase 2)

### Switch Branches

```bash
# List all branches
git branch -a

# Switch to main
git checkout main

# Switch to feature branch
git checkout feature/document-parser
```

---

---

## 🔧 Troubleshooting & Robust Startup

### Clean Startup (If server fails to start)
If you encounter "Address already in use" or the server fails to start:

```bash
# 1. Kill stale processes (Forceful Clean)
pkill -9 -f uvicorn
pkill -9 -f python

# 2. Start freshly
uv run uvicorn src.api.main:app --reload --port 8000
```

### Full Clean + Reinstall (robust restart)
Use this when dependencies are broken or the venv is corrupted. Data under `data/` is preserved.

```bash
cd option_2_platform
uv run python scripts/clean_env.py   # removes venv, caches, logs
uv venv
uv sync
uv run uvicorn src.api.main:app --reload --port 8000
# From repo root you can also run with --directory option_2_platform
```

### Frontend Stuck at "System wird gestartet..."

If the browser shows a loading screen with "System wird gestartet..." and doesn't proceed:

**1. Check Ollama is running:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama:
ollama serve
```

**2. Check Server Logs:**
Look for "Startup sequence finished" in the terminal.

---

## 📝 Development Principles

1. **Backend-First:** Implement core logic before UI
2. **Test-Driven:** Write tests before implementation
3. **Spec-Driven:** All work starts from specifications
4. **Privacy-First:** 100% local processing, no external APIs
5. **Modular:** Easy component replacement

---

## 🤝 Contributing

This is a private development project. For questions, contact the project team.

---

## 📄 License

Internal project - All rights reserved.
