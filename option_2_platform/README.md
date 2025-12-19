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

### Quick Command (macOS/Linux)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
cd option_2_platform
uv venv && uv sync
uv run pytest tests/ -v
```

### Start Frontend
The platform includes a web interface.
```bash
uv run uvicorn frontend.main:app --reload --port 8000
```
Open [http://localhost:8000](http://localhost:8000)

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

## 🔍 Troubleshooting

### Import Errors

```bash
# Ensure you're using uv run
uv run python script.py

# NOT: python script.py (uses system Python)
```

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve &
```

### Model Not Found

```bash
# List available models
ollama list

# Pull missing model
ollama pull qwen2.5:7b
```

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
