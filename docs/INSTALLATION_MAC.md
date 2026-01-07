# macOS Installation Guide

## 1. Install UV Package Manager

```bash
# Via curl (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew
brew install uv

# Verify installation
uv --version
```

## 2. Install LM Studio (primary)

Download and install from https://lmstudio.ai (enable the API server and keep it running on `http://localhost:1234`).

## 3. Install Ollama (fallback and for model pulls)

```bash
# Via Homebrew
brew install ollama

# Start Ollama server
ollama serve &

# Pull required model
ollama pull qwen2.5:7b
ollama pull qwen2.5:0.5b  # Optional: faster, smaller model
```

## 4. Clone Repository

```bash
git clone https://github.com/pzackert/Textverarbeitung.git
cd Textverarbeitung/option_2_platform
```

## 5. Setup Python Environment

```bash
# Create virtual environment
uv venv

# Install all dependencies (automatically activates venv)
uv sync

# Verify installation
uv run python -c "import src.ollama; print('✅ Imports working')"
```

## 6. Run Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific phase tests
uv run pytest tests/test_ollama/ -v
```

## 7. Start the Application (robust start)

```bash
# Ensure LM Studio (port 1234) or Ollama (port 11434) is running with a pulled model

# From project folder
cd Textverarbeitung/option_2_platform
uv run uvicorn src.api.main:app --reload --port 8000

# From repo root (alternative)
# uv --directory option_2_platform run uvicorn src.api.main:app --reload --port 8000
```

## 8. Full Reset & Reinstall (when startup fails)
Preserves `data/` but wipes virtual env, caches, and logs.

```bash
cd Textverarbeitung/option_2_platform
uv run python scripts/clean_env.py
uv venv
uv sync
uv run uvicorn src.api.main:app --reload --port 8000
```

## 9. Common macOS Issues

**Issue:** `ollama: command not found`
```bash
# Ensure Ollama is in PATH
export PATH="/opt/homebrew/bin:$PATH"
# Or restart terminal
```

**Issue:** `Metal acceleration not working`
```bash
# Check if running on Apple Silicon
uname -m  # Should show "arm64"
# Ollama automatically uses Metal on M1/M2/M3
```

**Issue:** `Port 8000 already in use` or Server fails to start
```bash
# Force kill stale python processes
pkill -9 -f uvicorn
pkill -9 -f python

# Restart server
uv run uvicorn src.api.main:app --reload --port 8000
```
