# Startup Analysis

## Scope
- Review current startup and health handling (no code changes).
- Identify gaps vs required robust, ordered startup with LM Studio/Ollama fallback and RAG preload.

## Observed Components
- FastAPI entry: [src/api/main.py](src/api/main.py) wires routers; no enforced startup sequencing or request blocking.
- System status/health: [src/api/routers/system.py](src/api/routers/system.py) exposes `/api/system/health`, `/api/system/status`, `/api/system/startup` (background task).
- Startup logic: [src/services/system_state.py](src/services/system_state.py#L52-L152) defines `run_startup_sequence()` and component status tracking.
- LLM provider: [src/rag/llm_provider.py](src/rag/llm_provider.py) only implements `OllamaProvider` (also used for LM Studio via OpenAI-compatible path if port 1234).
- LLM chain/config: [src/rag/llm_chain.py](src/rag/llm_chain.py), [src/rag/config.py](src/rag/config.py) (not fully reviewed here), dependencies via [src/api/dependencies.py](src/api/dependencies.py) or [src/services/system_state.py](src/services/system_state.py#L7-L49) (duplicate-ish helper functions there).
- RAG global load: [src/api/routers/rag_global.py](src/api/routers/rag_global.py) manual POST `/api/rag/global/load`; not part of startup sequence.
- Project unload: [src/api/routers/rag_project.py](src/api/routers/rag_project.py) manual; not part of startup sequence.
- Config: [config/config.yaml](config/config.yaml) currently defaults to `llm.provider: "lm_studio"`, `llm.base_url: http://127.0.0.1:1234`, model `mistralai/ministral-3-3b`; models_dir points to `~/.ollama/models` (inconsistent with LM Studio default path requirement).

## Current Startup Behavior (run_startup_sequence)
1. Marks `ollama` component as loading; constructs `OllamaProvider` with config.llm_base_url + model (assumes config.yaml). Retries availability up to 5 times; on failure sets error and returns early.
2. Marks `lm_studio` as ready without real probing (placeholder only).
3. Tests configured model via provider.test_connection; sets `llm_model` ready/error.
4. Initializes VectorStore (embedding + Chroma) and marks `embedding_model` + `chromadb` ready/error.
5. Forces `get_llm_chain()` to init pipeline; marks `rag_pipeline` ready/error.
6. No global RAG load; no model test prompt; no system-level lock/unlock of requests.

## Gaps vs Requirements
- No ordered check between LM Studio and Ollama; always treats provider as Ollama with possible OpenAI-compatible path; no fallback logic or clear error messaging chain.
- `lm_studio` status is hardcoded to ready; no reachability check for 127.0.0.1:1234.
- Config path mismatch: `llm.models_dir` points to Ollama path while provider `lm_studio` expected under ~/.lmstudio/models.
- No step to load or verify model file presence; only a tag lookup via provider.test_connection (Ollama/LMS openai list) but no fallback to alternate model.
- No "send OK prompt" validation step.
- No global knowledge load; RAG remains unloaded unless client calls `/api/rag/global/load`.
- No polling/progress exposure in `/api/system/status` beyond coarse component states; frontend polling guidance missing.
- No startup guard/middleware to block requests until ready.
- No handling for Chroma failure beyond marking error; server continues running without global status stop signal.
- No deterministic sequence enforcement from app startup; `run_startup_sequence` only triggered via POST /api/system/startup.

## Risks
- System may report ready while LM Studio is down (lm_studio set to ready unconditionally).
- If LM Studio unreachable but Ollama up on different port, current config will still fail early (base_url fixed) with no fallback to Ollama port 11434.
- RAG not preloaded, so first queries may have empty context despite "ready" status.
- Missing model test prompt could leave half-loaded model undetected.
- Request handling during initialization can proceed and hit partially initialized dependencies.

## Recommendations (for future implementation)
- Introduce dedicated startup service orchestrating ordered steps with retries, timeouts, and clear failure states.
- Add middleware guard to reject non-system requests while status != ready.
- Extend status payload with phase/progress and last error.
- Implement LM Studio and Ollama health probes separately; fallback logic based on config and availability.
- Verify model presence (local file) and run a short "OK" prompt.
- Auto-trigger global knowledge load and wait for ready.
- Align config defaults with required model directories and allow selecting backend/provider.
