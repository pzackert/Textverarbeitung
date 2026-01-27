# Installation & Setup

## Prerequisites
- **Python**: Version 3.10 or higher
- **Package Manager**: [uv](https://github.com/astral-sh/uv) (Required for deterministic dependency management)
- **Version Control**: Git

## Installation

1. **Clone Repository**
   ```bash
   git clone <repository_url>
   cd option_2_platform
   ```

2. **Install Dependencies**
   Use `uv` to sync the virtual environment exactly as defined in `uv.lock`. Do not use `pip install` manually.
   ```bash
   uv sync
   ```

## LLM Provider Setup

The system requires a local LLM provider.

### Option A: Ollama (Recommended)
1. Install [Ollama](https://ollama.com/).
2. Pull the default model:
   ```bash
   ollama pull qwen2.5:7b
   ```
3. Ensure Ollama is running on default port **11434**.

### Option B: LM Studio
1. Install [LM Studio](https://lmstudio.ai/).
2. Load a compatible model (e.g., Qwen 2.5 7B GGUF).
3. Start the Local Server on port **1234**.

## Configuration

1. The system uses `config/config.yaml` for defaults.
2. Ensure the `data/` directory is writable.
3. (Optional) Create a `.env` file if environment variable overrides are needed, though `config.yaml` is the primary source.

## Verifying Installation
Run the development server:
```bash
uv run uvicorn src.api.main:app --reload
```
Access the dashboard at [http://localhost:8000](http://localhost:8000).
