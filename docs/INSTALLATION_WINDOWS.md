# Windows Installation Guide

## 1. Install UV Package Manager

```powershell
# Via PowerShell (run as Administrator)
irm https://astral.sh/uv/install.ps1 | iex

# Or download from: https://github.com/astral-sh/uv/releases

# Verify installation
uv --version
```

## 2. Install Ollama

```powershell
# Download from: https://ollama.com/download/windows
# Run installer: OllamaSetup.exe

# Start Ollama (runs as service)
ollama serve

# Pull required model
ollama pull qwen2.5:7b
ollama pull qwen2.5:0.5b
```

## 3. Clone Repository

```powershell
git clone https://github.com/pzackert/Textverarbeitung.git
cd Textverarbeitung\option_2_platform
```

## 4. Setup Python Environment

```powershell
# Create virtual environment
uv venv

# Install all dependencies
uv sync

# Verify installation
uv run python -c "import src.ollama; print('✅ Imports working')"
```

## 5. Run Tests

```powershell
# Run all tests
uv run pytest tests\ -v

# Run specific phase tests
uv run pytest tests\test_ollama\ -v
```

## 6. Common Windows Issues

**Issue:** `uv: command not found`
```powershell
# Add UV to PATH manually
$env:Path += ";C:\Users\YourName\.local\bin"
# Or restart PowerShell/CMD
```

**Issue:** `Execution policy error`
```powershell
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```
