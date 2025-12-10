# Deployment Guide

## System Requirements

### Hardware
- **CPU:** 4+ Cores (Apple Silicon M1/M2/M3 recommended or modern Intel/AMD)
- **RAM:** 8GB minimum, 16GB recommended (for LLM + Vector Store)
- **Disk:** 20GB free space (Models: ~5GB, Data: ~1GB+)
- **GPU:** Optional but recommended for faster embeddings/inference.

### Software
- **OS:** macOS, Linux, or Windows (WSL2)
- **Python:** 3.10 or higher
- **Package Manager:** `uv` (recommended) or `pip`
- **LLM Host:** Ollama (installed and running)

## Installation Steps

1.  **Clone Repository**
    ```bash
    git clone <repo-url>
    cd option_2_platform
    ```

2.  **Install Dependencies**
    ```bash
    uv sync
    # OR
    pip install -r requirements.txt
    ```

3.  **Setup Ollama**
    - Install Ollama from [ollama.com](https://ollama.com)
    - Pull the model:
      ```bash
      ollama pull qwen2.5:7b
      ```
    - Start the service:
      ```bash
      ollama serve
      ```

4.  **Configuration**
    - Check `config/config.yaml`.
    - Ensure `llm_base_url` matches your Ollama instance (default: `http://localhost:11434`).

5.  **Ingest Documents**
    - Place PDF/DOCX files in `data/input`.
    - Run ingestion:
      ```bash
      uv run python examples/ingest_test_documents.py
      ```

6.  **Run Demo**
    ```bash
    uv run python examples/rag_demo.py
    ```

## Production Checklist

- [ ] **Persistence:** Ensure `data/chromadb` is backed up.
- **Logging:** Logs are written to `logs/` (if configured) or stdout.
- **Security:** Ensure Ollama is not exposed to public internet (bind to localhost).
- **Monitoring:** Check `examples/performance_benchmark.py` periodically.

## Troubleshooting

- **Connection Refused:** Check if `ollama serve` is running.
- **Model Not Found:** Run `ollama list` to verify `qwen2.5:7b` is installed.
- **Memory Errors:** Reduce `chunk_size` in config or use a smaller model (e.g., `qwen2.5:1.5b`).
