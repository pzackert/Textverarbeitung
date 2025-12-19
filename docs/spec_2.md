# Ollama/LM Studio Integration - Specification

## Goal
Establish a robust, local-first LLM integration layer that abstracts differences between Ollama and LM Studio, providing a unified async API for the platform.

## Requirements

### Functional
- [ ] **Provider Detection**: Automatically detect if Ollama or LM Studio is running on default ports (11434 vs 1234).
- [ ] **Service Management**: Scripts to start/stop the LLM service on macOS (bash) and Windows (PowerShell).
- [ ] **Health Checks**: `check_connection()` method returning status and latency.
- [ ] **Model Management**: List available models and validate selected model exists.
- [ ] **Token Counting**: Accurate token estimation for Qwen models (using tiktoken or similar approximation if exact tokenizer unavailable).
- [ ] **Streaming**: Support `AsyncIterator` response for real-time UI feedback.
- [ ] **Timeout Handling**: Configurable timeouts (default 30s) with specific `LLMTimeoutError`.

### Non-Functional
- [ ] **Local-First**: Zero external internet calls required for inference.
- [ ] **Performance**: Connection check < 100ms.
- [ ] **Reliability**: Automatic retry logic (3 attempts) for transient failures.
- [ ] **Compatibility**: Full support for `qwen2.5:7b` and `qwen2.5:3b`.

## Input/Output Definitions

### Configuration (`config/ollama.toml`)
```toml
[llm]
provider = "ollama" # or "lm_studio"
base_url = "http://localhost:11434"
model = "qwen2.5:7b"
timeout = 30
max_retries = 3
temperature = 0.7

[llm.fallback]
enabled = true
provider = "lm_studio"
base_url = "http://localhost:1234/v1"
```

### Client Interface (`src/ollama/client.py`)
```python
class LLMClient:
    async def connect(self) -> bool:
        """Establishes connection and verifies provider is reachable."""
        ...
    
    async def list_models(self) -> List[str]:
        """Returns list of available model names from provider."""
        ...
    
    async def generate(
        self, 
        prompt: str, 
        system: Optional[str] = None,
        temperature: float = 0.7
    ) -> str:
        """Generates a complete response string."""
        ...
    
    async def generate_stream(
        self, 
        prompt: str, 
        system: Optional[str] = None
    ) -> AsyncIterator[str]:
        """Yields response chunks for real-time display."""
        ...
    
    def count_tokens(self, text: str) -> int:
        """Estimates token count for input text."""
        ...
```

## Test Cases

| ID | Name | Description | Expected Result |
|----|------|-------------|-----------------|
| TC-LLM-01 | **Connection Check** | Call `connect()` when server is running | Returns `True`, latency < 100ms |
| TC-LLM-02 | **Hello World** | Send "Say 'Hello'" prompt | Response contains "Hello" |
| TC-LLM-03 | **Model Listing** | Call `list_models()` | Returns list containing `qwen2.5:7b` |
| TC-LLM-04 | **Timeout Handling** | Simulate 31s delay | Raises `LLMTimeoutError` |
| TC-LLM-05 | **Token Counting** | Count tokens in "Hello world" | Returns integer approx 2-3 |
| TC-LLM-06 | **Streaming** | Request stream for long text | Yields chunks, final text matches non-stream |
| TC-LLM-07 | **Service Start** | Run `start_ollama.sh` | Process starts, port 11434 active |

## Success Criteria
- [ ] All 7 test cases pass in CI environment (or local dev).
- [ ] `uv run pytest tests/test_ollama` executes without errors.
- [ ] No dependency on `openai` python package (use raw `httpx` for control).
- [ ] Documentation covers switching between Ollama and LM Studio.

## Dependencies
- `httpx` (Async HTTP client)
- `pydantic` (Configuration validation)
- `tenacity` (Retry logic)

## Files to Create
- `src/ollama/client.py`
- `src/ollama/exceptions.py`
- `src/ollama/config.py`
- `src/ollama/service_manager.py`
- `scripts/start_ollama.sh`
- `scripts/start_ollama.ps1`
- `tests/test_ollama/test_connection.py`
- `tests/test_ollama/test_generation.py`
