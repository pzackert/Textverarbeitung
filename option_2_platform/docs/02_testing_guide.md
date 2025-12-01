# Testing Guide - Option 2 Platform

Complete guide to testing the IFB PROFI Option 2 platform.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Running Tests](#running-tests)
- [Test Organization](#test-organization)
- [Manual Testing](#manual-testing)
- [Troubleshooting](#troubleshooting)

---

## Overview

The Option 2 platform uses **PyTest** for automated testing with a modular, phase-based test structure matching the source code organization.

### Test Coverage

| Phase | Component | Status | Location |
|-------|-----------|--------|----------|
| 1 | Ollama Integration | ✅ | `tests/test_ollama/` |
| 2 | Document Parsing | ⏳ | `tests/test_parsers/` |
| 3 | RAG System | ⏳ | `tests/test_rag/` |
| 4 | Criteria Engine | ⏳ | `tests/test_criteria/` |
| 5 | API Layer | ⏳ | `tests/test_api/` |
| 6 | UI Integration | ⏳ | `tests/test_ui/` |

---

## Prerequisites

### 1. Environment Setup

```bash
# Ensure virtual environment is active
cd /path/to/option_2_platform

# Create venv if not exists
uv venv

# Install all dependencies including test dependencies
uv sync
```

### 2. Ollama Setup

```bash
# Start Ollama server
ollama serve &

# Pull test models
ollama pull qwen2.5:7b
ollama pull qwen2.5:0.5b
```

### 3. Verify Installation

```bash
# Check PyTest is installed
uv run pytest --version

# Verify imports work
uv run python -c "import src.ollama; print('✅')"
```

---

## Running Tests

### Run All Tests

```bash
# Verbose mode
uv run pytest tests/ -v

# With output capture disabled (see print statements)
uv run pytest tests/ -v -s

# Generate HTML report
uv run pytest tests/ -v --html=logs/test_report.html --self-contained-html
```

### Run Specific Phase

```bash
# Phase 1: Ollama Integration
uv run pytest tests/test_ollama/ -v

# Phase 2: Document Parsing
uv run pytest tests/test_parsers/ -v

# Phase 3: RAG System
uv run pytest tests/test_rag/ -v

# Phase 4: Criteria Engine
uv run pytest tests/test_criteria/ -v
```

### Run Specific Test File

```bash
uv run pytest tests/test_ollama/test_infrastructure.py -v
```

### Run Specific Test Function

```bash
uv run pytest tests/test_ollama/test_infrastructure.py::test_placeholder -v
```

### Run with Markers

```bash
# Run only unit tests
uv run pytest tests/ -v -m unit

# Run only integration tests
uv run pytest tests/ -v -m integration

# Skip slow tests
uv run pytest tests/ -v -m "not slow"
```

---

## Test Organization

### Directory Structure

```
tests/
├── conftest.py                 # Shared fixtures and configuration
├── fixtures/                   # Test data and mock files
├── test_ollama/               # LLM integration tests
│   ├── test_infrastructure.py
│   ├── test_client.py
│   └── test_model_switching.py
├── test_parsers/              # Document parsing tests
│   ├── test_pdf_parser.py
│   ├── test_docx_parser.py
│   └── test_xlsx_parser.py
├── test_rag/                  # RAG system tests
│   ├── test_ingestion.py
│   ├── test_retrieval.py
│   └── test_embeddings.py
└── test_criteria/             # Criteria engine tests
    ├── test_engine.py
    └── test_toon_parser.py
```

### Test Naming Conventions

- **Test files:** `test_<module>.py`
- **Test functions:** `test_<feature>_<scenario>()`
- **Test classes:** `Test<Module>`

**Examples:**
```python
# Good
def test_ollama_connection_success():
    ...

def test_pdf_parser_handles_corrupt_file():
    ...

# Bad
def test1():
    ...

def check_connection():  # Missing 'test_' prefix
    ...
```

---

## Manual Testing

### LLM Connection Test

```bash
uv run python -c "
from src.ollama.client import OllamaClient

# Test basic connection
client = OllamaClient()
print('✅ Connected to Ollama')

# Test simple generation
response = client.generate('Say hello in one word', max_tokens=5)
print(f'Response: {response}')
"
```

**Expected Output:**
```
✅ Connected to Ollama
Response: Hi!
```

---

### Model Switching Test

```bash
uv run python -c "
from src.ollama.client import OllamaClient
import time

client = OllamaClient()

# Test qwen2.5:7b
print('Testing qwen2.5:7b...')
client.model_name = 'qwen2.5:7b'
start = time.time()
response1 = client.generate('Hello', max_tokens=5)
time1 = time.time() - start
print(f'7b: {response1} ({time1:.2f}s)')

# Test qwen2.5:0.5b
print('Testing qwen2.5:0.5b...')
client.model_name = 'qwen2.5:0.5b'
start = time.time()
response2 = client.generate('Hello', max_tokens=5)
time2 = time.time() - start
print(f'0.5b: {response2} ({time2:.2f}s)')

print(f'Speed improvement: {time1/time2:.1f}x')
"
```

**Expected Output:**
```
Testing qwen2.5:7b...
7b: Hi! (0.47s)
Testing qwen2.5:0.5b...
0.5b: Hi! (0.19s)
Speed improvement: 2.5x
```

---

### Performance Benchmark Test

```bash
uv run python -c "
from src.ollama.client import OllamaClient
import time

client = OllamaClient()
prompt = 'Explain Python in 10 words'

print('Running 10 requests...')
times = []
for i in range(10):
    start = time.time()
    response = client.generate(prompt, max_tokens=20)
    elapsed = time.time() - start
    times.append(elapsed)
    print(f'{i+1}. {elapsed:.2f}s')

avg = sum(times) / len(times)
print(f'\nAverage: {avg:.2f}s')
print(f'Min: {min(times):.2f}s | Max: {max(times):.2f}s')
print(f'Throughput: {60/avg:.1f} req/min')
"
```

**Expected Output (Apple M1 Pro):**
```
Running 10 requests...
1. 2.78s  # First request (warmup)
2. 0.47s
3. 0.47s
...
10. 0.45s

Average: 0.71s
Min: 0.45s | Max: 2.78s
Throughput: 84.4 req/min
```

---

### Configuration Test

```bash
# Test reading configuration
uv run python -c "
import toml
config = toml.load('config/ollama.toml')
print('Provider:', config['ollama']['provider'])
print('Base URL:', config['ollama']['base_url'])
print('Default Model:', config['ollama']['default_model'])
print('Max Tokens:', config['generation']['max_tokens'])
"
```

---

## Troubleshooting

### Test Discovery Issues

**Problem:** PyTest can't find tests

```bash
# Check if tests are discovered
uv run pytest --collect-only

# Ensure you're in project root
pwd  # Should end with option_2_platform

# Verify test files start with 'test_'
ls tests/test_ollama/
```

---

### Import Errors

**Problem:** `ModuleNotFoundError: No module named 'src'`

```bash
# Always use 'uv run' prefix
uv run pytest tests/ -v

# NOT: pytest tests/ -v
```

**Problem:** `ImportError: cannot import name 'OllamaClient'`

```bash
# Verify module exists
uv run python -c "from src.ollama.client import OllamaClient; print('✅')"

# Check file exists
ls -la src/ollama/client.py
```

---

### Ollama Connection Errors

**Problem:** Tests fail with connection timeout

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama if not running
ollama serve &

# Wait a few seconds
sleep 3

# Verify models are available
ollama list
```

**Problem:** Model not found

```bash
# Pull missing model
ollama pull qwen2.5:7b
ollama pull qwen2.5:0.5b

# Verify download
ollama list
```

---

### Test Failures

**Problem:** Assertion errors

1. Read the error message carefully
2. Check test expectations match actual behavior
3. Verify test data/fixtures are correct
4. Run test in verbose mode: `pytest tests/ -vv`
5. Add print statements: `pytest tests/ -s`

**Problem:** Timeout errors

1. Increase timeout in test
2. Use smaller model (qwen2.5:0.5b)
3. Reduce max_tokens parameter
4. Check system resources (CPU/Memory/GPU)

---

### Performance Issues

**Problem:** Tests are very slow

```bash
# Run tests in parallel (if possible)
uv run pytest tests/ -n auto

# Use faster model for testing
# Edit config/ollama.toml:
# default_model = "qwen2.5:0.5b"

# Skip slow tests
uv run pytest tests/ -m "not slow"
```

---

## Test Results Interpretation

### Successful Run

```
============================== test session starts ==============================
platform darwin -- Python 3.12.11, pytest-9.0.1, pluggy-1.6.0
rootdir: /Users/patrick.zackert/projects/masterprojekt/option_2_platform
configfile: pyproject.toml
collected 1 item

tests/test_ollama/test_infrastructure.py::test_placeholder PASSED        [100%]

============================== 1 passed in 0.03s ===============================
```

✅ All tests passed successfully

---

### Test Failure

```
============================== test session starts ==============================
...
tests/test_ollama/test_connection.py::test_ollama_connect FAILED         [100%]

================================== FAILURES =====================================
____________________________ test_ollama_connect _______________________________

    def test_ollama_connect():
        client = OllamaClient()
>       assert client.connect() == True
E       AssertionError: assert False == True

tests/test_ollama/test_connection.py:5: AssertionError
============================== 1 failed in 0.05s ================================
```

❌ Test failed - check Ollama server is running

---

### Test Skipped

```
============================== test session starts ==============================
...
tests/test_parsers/test_pdf.py::test_ocr_fallback SKIPPED (OCR not inst[100%]

============================== 1 skipped in 0.01s ===============================
```

⏭️ Test skipped - optional dependency not installed

---

## Expected Test Results

### Current Status (Phase 1 Complete)

```bash
$ uv run pytest tests/ -v

collected 1 item

tests/test_ollama/test_infrastructure.py::test_placeholder PASSED        [100%]

============================== 1 passed in 0.03s ===============================
```

### Future Status (All Phases Complete)

```bash
$ uv run pytest tests/ -v

collected 45 items

tests/test_ollama/test_infrastructure.py::test_placeholder PASSED        [  2%]
tests/test_ollama/test_client.py::test_connection PASSED                 [  4%]
tests/test_ollama/test_client.py::test_generation PASSED                 [  6%]
tests/test_parsers/test_pdf_parser.py::test_extract_text PASSED          [  8%]
tests/test_parsers/test_pdf_parser.py::test_extract_tables PASSED        [ 11%]
tests/test_parsers/test_docx_parser.py::test_extract_text PASSED         [ 13%]
tests/test_rag/test_ingestion.py::test_ingest_document PASSED            [ 15%]
tests/test_rag/test_retrieval.py::test_semantic_search PASSED            [ 17%]
tests/test_criteria/test_engine.py::test_evaluate_criterion PASSED       [ 20%]
...

============================== 45 passed in 12.34s ==============================
```

---

## Continuous Testing

### Watch Mode (Development)

```bash
# Install pytest-watch
uv pip install pytest-watch

# Run tests on file changes
uv run ptw tests/ -- -v
```

### Pre-Commit Testing

```bash
# Run tests before committing
git add .
uv run pytest tests/ -v && git commit -m "Your message"
```

---

## Additional Resources

- **[PyTest Documentation](https://docs.pytest.org/):** Official PyTest docs
- **[Project Constitution](../specs/constitution.md):** Testing principles
- **[LLM Integration Report](../logs/llm_integration_test_summary.txt):** Performance metrics

---

## Quick Reference

```bash
# Run all tests
uv run pytest tests/ -v

# Run specific phase
uv run pytest tests/test_ollama/ -v

# Run with coverage
uv run pytest tests/ --cov=src --cov-report=html

# Run specific test
uv run pytest tests/test_ollama/test_infrastructure.py::test_placeholder -v

# Run and see output
uv run pytest tests/ -v -s

# Stop on first failure
uv run pytest tests/ -v -x

# Show local variables on failure
uv run pytest tests/ -v -l
```

---

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review test output carefully
3. Verify environment setup
4. Contact project team

---

**Last Updated:** 2025-12-01  
**Test Framework:** PyTest 9.0.1  
**Python Version:** 3.12.11
