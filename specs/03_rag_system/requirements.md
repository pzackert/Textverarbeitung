# Requirements (Phase 3)

## 1. Python Packages
Hinzufügen zu `pyproject.toml` oder via `uv add`:

```toml
[project.dependencies]
chromadb = "^0.4.22"
sentence-transformers = "^2.3.1"
numpy = "^1.26.0"
pydantic = "^2.6.0"
# Bereits vorhanden
ollama = "^0.1.6"
pymupdf = "^1.23.8"
python-docx = "^1.1.0"
openpyxl = "^3.1.2"
```

## 2. External Services
- **Ollama**: Version 0.1.20+
- **Modelle**:
    - `qwen2.5:7b` (Produktion)
    - `qwen2.5:0.5b` (Testing)
- **LM Studio** (Optional): Als Alternative.

## 3. Hardware Requirements
- **RAM**: Minimum 8GB (16GB empfohlen für 7b Model).
- **Disk Space**: ~2GB für Embedding Models + Vector Store + LLM Models.
- **CPU**: AVX2 Support empfohlen.
- **GPU**: Optional (Metal auf Mac M1/M2/M3 unterstützt).

## 4. Installation Order
1. `uv sync` (Basis-Dependencies)
2. `ollama pull qwen2.5:7b` (LLM Model)
3. `uv run python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')"` (Embedding Model Download)

