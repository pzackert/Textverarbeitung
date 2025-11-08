# LLM Integration
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 8. November 2025

## Übersicht

Integration und Management des lokalen LLM-Systems für die Dokumentenanalyse basierend auf LM Studio.

## Systemkonfiguration

Die gesamte Systemkonfiguration wird in einer zentralen JSON-Datei verwaltet:

```json
{
    "llm": {
        "engine": "lm_studio",
        "model": {
            "name": "mistral-7b-instruct-v0.2",
            "path": "/path/to/models/mistral-7b-instruct-v0.2.Q4_K_M.gguf",
            "format": "gguf",
            "quantization": "Q4_K_M",
            "context_window": 8192,
            "max_tokens": 4096
        },
        "inference": {
            "temperature": 0.1,
            "top_p": 0.9,
            "frequency_penalty": 0.0,
            "presence_penalty": 0.0,
            "stop_tokens": ["</answer>", "Human:", "Assistant:"],
            "cache_size": 1024,
            "batch_size": 8
        },
        "api": {
            "host": "localhost",
            "port": 1234,
            "timeout": 30
        }
    },
    "vector_store": {
        "engine": "chroma",
        "path": "/path/to/chromadb",
        "embedding_model": "BAAI/bge-large-en-v1.5",
        "dimension": 1024,
        "collection_settings": {
            "hnsw_space": "cosine",
            "hnsw_ef_construction": 100,
            "hnsw_m": 16
        }
    },
    "rag": {
        "chunk_size": 1000,
        "chunk_overlap": 200,
        "max_chunks_per_query": 5,
        "similarity_threshold": 0.75
    }
}

## Prompting-Strategie

Für jede Kriterienprüfung wird ein neuer Chat mit spezifischem Kontext erstellt:

### Basis-Prompt-Template
```text
<|system|>
Du bist ein Experte für die Prüfung von Förderanträgen. Analysiere die gegebenen 
Informationen sorgfältig und antworte präzise auf die Frage.

<|context|>
{retrieved_context}

<|human|>
{specific_question}

<|assistant|>
```

### Antwortformat
```json
{
    "kriterium": "string",
    "erfuellt": true|false,
    "wert": "string|number|boolean",
    "begruendung": "string",
    "quellen": ["string"],
    "confidence": 0.0-1.0
}
```

## Technische Integration

### LM Studio Setup
1. Modell-Download und Quantisierung
   ```bash
   # Beispiel für Mistral 7B
   wget https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/resolve/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf
   ```

2. LM Studio Server starten
   ```bash
   lmstudio --model /path/to/model.gguf --host 0.0.0.0 --port 1234
   ```

3. API-Integration
   ```python
   from llm_client import LMStudioClient
   
   client = LMStudioClient("config.json")
   response = client.create_completion(
       prompt="Prüfe anhand des Kontexts...",
       context="Relevante Dokumente..."
   )

### Anforderungen
- Modellgröße: 7B - 13B Parameter
- Quantisierung: 4-bit
- GGUF Format
- Kontext: min. 8k Tokens

### Deployment
- Lokaler Inference Server
- REST API
- Konfigurierbare Endpunkte

## Prompt Engineering

### Basisstruktur
```text
SYSTEM: Du bist ein Experte für Förderanträge...
CONTEXT: {retrieved_context}
QUERY: {specific_question}
```

### Prompt-Typen
1. Kriterienprüfung
2. Datenextraktion
3. Validierung
4. Zusammenfassung

## Inferenz-Pipeline

### Ablauf
1. Kontext aus RAG
2. Prompt-Generierung
3. LLM-Anfrage
4. Antwortverarbeitung

### Parameter
- Temperature: 0.1
- Top-P: 0.9
- Max Tokens: 2048
- Stop Tokens: konfigurierbar

## Performance & Optimierung

### Hardware-Anforderungen
- CPU: 8+ Kerne
- RAM: 16GB+ (32GB empfohlen)
- GPU: Optional, CUDA-fähig
- SSD: 50GB+ für Modelle

### Caching-Strategien
```python
{
    "cache_config": {
        "type": "redis",
        "host": "localhost",
        "port": 6379,
        "db": 0,
        "ttl": 86400,  # 24h
        "max_size": "2gb"
    }
}
```

### Monitoring & Logging
- Prometheus Metriken
- Token-Verbrauch
- Antwortzeiten
- Fehlerraten
- Cache-Hits/Misses

## Integration mit Vector Store

### ChromaDB Konfiguration
```python
from chromadb import Client, Settings

client = Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory="db",
    anonymized_telemetry=False
))

# Collection pro Projekt
collection = client.create_collection(
    name=f"projekt_{projekt_id}",
    metadata={
        "embedding_model": "BAAI/bge-large-en-v1.5",
        "embedding_dim": 1024
    }
)
```

### RAG-Pipeline
```python
def process_query(query: str, projekt_id: str) -> dict:
    # 1. Relevante Dokumente finden
    context = vector_store.search(
        query=query,
        k=config["rag"]["max_chunks_per_query"]
    )
    
    # 2. LLM-Anfrage mit Kontext
    response = llm_client.create_completion(
        prompt=query,
        context="\n\n".join(context)
    )
    
    return response
```

## Fehlerbehandlung

### Retry-Mechanismus
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10)
)
def llm_request_with_retry(*args, **kwargs):
    return llm_client.create_completion(*args, **kwargs)
```

### Fallback-Strategien
1. Alternative Modelle
2. Cache-Nutzung
3. Manuelle Prüfung