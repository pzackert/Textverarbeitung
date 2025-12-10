# Admin Guide

## System Management

### Starting the System

To start the platform with all checks enabled:

```bash
python scripts/start_app.py
```

This script performs the following checks:
1. **Directories:** Ensures `data/`, `logs/`, etc. exist.
2. **Ollama:** Checks if Ollama is running and the configured model is loaded.
3. **ChromaDB:** Checks if the vector database is accessible.

### Sample Data Management

The platform includes a sample data generator for testing and demonstration purposes.

#### Generating & Loading Sample Data

**Via UI:**
1. Go to the Dashboard.
2. Scroll down to "Admin Actions".
3. Click "Load Sample Data".
4. Wait for the "Success" message.

**Via CLI:**
```bash
# Generate files
python scripts/generate_sample_data.py

# Ingest into DB
python scripts/ingest_samples.py
```

#### Clearing Data

To clear the vector database, simply delete the `data/chromadb` directory and restart the application (or re-run ingestion).

```bash
rm -rf data/chromadb
```

### Configuration

The system configuration is located in `config/config.yaml`.
Key settings:
- `llm.model`: The Ollama model to use (e.g., `qwen2.5:7b`).
- `rag.chunk_size`: Size of text chunks for retrieval.
- `rag.top_k`: Number of chunks to retrieve per query.

### Logs

Application logs are written to `logs/app.log` (if configured) and printed to stdout.
Check logs for:
- Ingestion errors
- LLM connection issues
- API errors
