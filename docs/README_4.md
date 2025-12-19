# IFB PROFI RAG API

REST API layer for the IFB Document Analysis System.

## Overview

This API exposes the RAG (Retrieval-Augmented Generation) backend capabilities via standard REST endpoints.

## Getting Started

### Prerequisites
- Python 3.10+
- Dependencies installed (`uv sync` or `pip install -r requirements.txt`)
- Ollama running locally
- ChromaDB initialized

### Start the Server
```bash
# Using the script
python scripts/start_api.py

# Or directly with uvicorn
uvicorn src.api.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`.
Documentation (Swagger UI) is at `http://localhost:8000/docs`.

## Endpoints

### Ingestion
- `POST /api/v1/ingest/upload`: Upload and process a document (PDF, DOCX, XLSX).

### Query
- `POST /api/v1/query`: Ask a question to the RAG system.
  ```json
  {
    "question": "What are the funding requirements?",
    "template_type": "standard",
    "top_k": 5
  }
  ```

### System
- `GET /api/v1/system/health`: Check system status (Ollama, ChromaDB).
- `GET /api/v1/system/config`: Get current configuration.
- `GET /api/v1/system/stats`: Get system statistics.

## Error Handling
The API uses standard HTTP status codes:
- 200: Success
- 400: Bad Request (Invalid input)
- 500: Internal Server Error (Processing failed)
