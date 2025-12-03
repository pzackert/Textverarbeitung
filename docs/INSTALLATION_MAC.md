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

## 2. Install Ollama

```bash
# Via Homebrew
brew install ollama

# Start Ollama server
ollama serve &

# Pull required model
ollama pull qwen2.5:7b
ollama pull qwen2.5:0.5b  # Optional: faster, smaller model
```

## 3. Clone Repository

```bash
git clone https://github.com/pzackert/Textverarbeitung.git
cd Textverarbeitung/option_2_platform
```

## 4. Setup Python Environment

```bash
# Create virtual environment
uv venv

# Install all dependencies (automatically activates venv)
uv sync

# Verify installation
uv run python -c "import src.ollama; print('✅ Imports working')"
```

## 5. Run Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific phase tests
uv run pytest tests/test_ollama/ -v
```

## 6. Common macOS Issues

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
