# Installation

## Voraussetzungen

- Python 3.11+
- UV Package Manager

## Setup

### 1. UV installieren

**macOS/Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Windows:**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Projekt Setup
```bash
cd option_2_platform
uv sync
```

### 3. Ollama Setup (für LLM)
```bash
# Ollama installieren
curl -fsSL https://ollama.com/install.sh | sh

# Model laden
ollama pull qwen2.5:7b
```

### 4. App starten
```bash
uv run python scripts/start_app.py
```

Öffne: http://localhost:8001

## ⚠️ WICHTIG: Nutze IMMER `uv run`

**FALSCH:**
```bash
python script.py
python3 script.py
source venv/bin/activate && python script.py
```

**RICHTIG:**
```bash
uv run python script.py
uv run pytest
uv run scripts/start_app.py
```