# Requirements (Phase 3)

## 1. Python Packages
Add these to `pyproject.toml` or install via `uv add`:

```toml
[project.dependencies]
chromadb = "^0.4.22"
sentence-transformers = "^2.3.1"
numpy = "^1.26.0"
pydantic = "^2.6.0"
# Existing dependencies
ollama = "^0.1.6"
pymupdf = "^1.23.8"
python-docx = "^1.1.0"
openpyxl = "^3.1.2"
```

## 2. LLM Requirements
- **Ollama**: Version 0.1.20+
- **Models**:
    - `qwen2.5:7b` (Production)
    - `qwen2.5:0.5b` (Testing)
- **RAM**: Minimum 8GB (16GB recommended for 7b model).

## 3. Hardware Requirements
- **Disk Space**: ~2GB for Embedding Models + Vector Store.
- **CPU**: AVX2 support recommended for vector operations.
- **GPU**: Optional (Metal on Mac M1/M2/M3 supported by Ollama).

## 4. Compatibility Matrix
| Component | Version | Notes |
|-----------|---------|-------|
| Python | 3.12 | Required |
| ChromaDB | 0.4.x | 0.5.x has breaking changes, stick to stable |
| Pydantic | v2 | Strict typing |
