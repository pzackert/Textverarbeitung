# Backend Settings Changes

## Config Schema (config/config.yaml)
- `llm`: {provider, model, temperature, max_tokens, timeout, lm_studio{models_dir, endpoint}, ollama{models_dir, endpoint}}
- `rag`: {chunk_size, chunk_overlap, embedding_model, top_k, similarity_threshold, persist_directory, collection_name, include_scores, max_context_chunks}
- `prompts`: {begruessung, global_chat_initial, antrags_chat_initial, antwort_richtlinie, kriterien_pruefung}

## Startup Model Scan
- On startup, models are scanned in both `llm.lm_studio.models_dir` and `llm.ollama.models_dir` (filename-based).
- Provider selection prefers configured provider if available; otherwise falls back to available backend.

## API Endpoints (backend)
- GET `/api/settings`: returns config + `available_models`.
- GET `/api/settings/models`: list all scanned models [{name, provider, size}].
- POST `/api/settings/llm`: {provider?, model, temperature, max_tokens, timeout} → writes config, restart required.
- POST `/api/settings/rag`: {chunk_size, chunk_overlap, top_k} → writes config, restart required.
- POST `/api/settings/prompts`: all prompt fields → writes config, restart required.
- GET `/api/settings/chromadb/info`: {version, persist_directory, storage_mb, total_chunks, status}.
- Global Knowledge:
  - POST `/api/settings/global-knowledge/upload` (multipart file) → saves and hot-adds to RAG, returns chunk count.
  - GET `/api/settings/global-knowledge/files` → [{filename, size_bytes, chunks, modified_ts}].
  - DELETE `/api/settings/global-knowledge/{filename}` → removes file and chunks.

## Restart Semantics
- LLM/RAG/Prompts POST: persist config, requires manual restart to take effect.
- Global Knowledge: hot-add, no restart needed.

## Frontend Notes
- New navigation entry “Einstellungen” can consume these endpoints directly.
- Model dropdown uses GET `/api/settings/models` (display name + provider).
- After save: show toast “System-Neustart erforderlich”. Optional “System jetzt neu starten” button can call existing `/api/system/startup`.
- Display read-only paths: lm_studio.models_dir, ollama.models_dir, embedding_model.

## Testing
- New tests in `tests/test_api/test_settings.py` cover config read/write and models listing. Requires pytest installed in env.
