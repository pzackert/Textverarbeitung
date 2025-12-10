# Testing Guide

Comprehensive guide to the test suite, running tests, and writing new tests.

## Table of Contents

1. [Overview](#overview)
2. [Running Tests](#running-tests)
3. [Test Categories](#test-categories)
4. [Test Structure](#test-structure)
5. [Writing New Tests](#writing-new-tests)
6. [Fixtures and Helpers](#fixtures-and-helpers)
7. [Troubleshooting](#troubleshooting)
8. [CI/CD Integration](#cicd-integration)
9. [Coverage Reports](#coverage-reports)

---

## Overview

The test suite provides comprehensive coverage across multiple layers:

### Test Summary

| Category | Test Count | Status | Purpose |
|----------|-----------|--------|---------|
| **test_general** | 23 | ✅ New | System health, error handling |
| **test_api** | 5 | ✅ Stable | API endpoint testing |
| **test_criteria** | 13 | ✅ New | K001-K006 business logic |
| **test_integration** | 4 | ⚠️ Partial | Multi-component workflows |
| **test_rag** | 60 | ✅ Excellent | RAG pipeline components |
| **test_parsers** | 15 | ✅ Stable | Document parsing |
| **test_ollama** | 1 | ⚠️ Minimal | LLM integration |
| **test_benchmarks** | Special | 🔧 Separate | Performance benchmarking |
| **TOTAL** | **121** | 97%+ | Comprehensive coverage |

### Current Status

```
Total Tests: 121 (including benchmarks separately)
Passing: 115+ (97%+)
Known Failures: 2 (test_integration - route issues)
Coverage: ~80%+ (varies by module)
```

### Architecture

```
Backend Architecture Layers:
┌─────────────────────────────────────────┐
│  API Layer (FastAPI)                    │  → test_api/
├─────────────────────────────────────────┤
│  RAG Pipeline (Chunking, Embeddings)    │  → test_rag/
├─────────────────────────────────────────┤
│  LLM Integration (Ollama)               │  → test_ollama/
├─────────────────────────────────────────┤
│  Document Parsing (PDF, DOCX, XLSX)     │  → test_parsers/
├─────────────────────────────────────────┤
│  Business Logic (K001-K006 Criteria)    │  → test_criteria/
├─────────────────────────────────────────┤
│  System Health (Deployment, Errors)     │  → test_general/
├─────────────────────────────────────────┤
│  Integration (E2E Workflows)            │  → test_integration/
├─────────────────────────────────────────┤
│  Performance (Benchmarks)               │  → test_benchmarks/
└─────────────────────────────────────────┘
```

---

## Running Tests

### Quick Start

```bash
# Run all tests (excluding benchmarks)
uv run pytest tests/ --ignore=tests/test_benchmarks -v

# Run specific test category
uv run pytest tests/test_api/ -v
uv run pytest tests/test_rag/ -v
uv run pytest tests/test_general/ -v

# Run specific test file
uv run pytest tests/test_api/test_endpoints.py -v

# Run specific test
uv run pytest tests/test_api/test_endpoints.py::test_root_endpoint -v
```

### Common Commands

**Run with stop on first failure:**
```bash
uv run pytest tests/ --ignore=tests/test_benchmarks -x -v
```

**Run with detailed output:**
```bash
uv run pytest tests/ --ignore=tests/test_benchmarks -vv
```

**Run in quiet mode (fewer output):**
```bash
uv run pytest tests/ --ignore=tests/test_benchmarks -q
```

**Run tests matching pattern:**
```bash
uv run pytest tests/ -k "api" -v
uv run pytest tests/ -k "error" -v
uv run pytest tests/ -k "k001 or k002" -v
```

**Run with markers:**
```bash
uv run pytest tests/ -m unit -v
uv run pytest tests/ -m integration -v
```

**Skip slow tests:**
```bash
uv run pytest tests/ -m "not slow" -v
```

### Benchmark Suite

The benchmark suite is separate and runs differently:

```bash
# Run benchmark suite
cd tests/test_benchmarks/
uv run python test_suite.py

# Run benchmarks for specific model
# (Edit test_suite.py or run interactively)

# View benchmark results
cat results/run_*.json | python -m json.tool
```

**Benchmark Results Location:**
```
tests/test_benchmarks/results/run_2025-12-08_*.json
```

---

## Test Categories

### test_general/ - System Health & Error Handling

**Purpose:** Deployment readiness and error resilience

**Test Classes:**
- `TestOllamaAvailability` - Ollama service running and accessible
- `TestOllamaModelInstalled` - Required models available
- `TestDiskSpaceAvailable` - Sufficient disk space for operations
- `TestChromaDBAccessible` - Vector store connectivity
- `TestProjectDirectoriesExist` - Required directories present
- `TestModelResponds` - LLM responds within time limits
- `TestEmptyProjectGracefulHandling` - Graceful empty project handling
- `TestInvalidPDFHandling` - Corrupt/invalid PDF handling
- `TestQueryTimeout` - Query timeout handling
- `TestMissingModelHandling` - Missing model error handling
- `TestChromaDBConnectionFailure` - DB connection failure handling
- `TestEmptyDocumentSet` - Empty document set handling
- `TestLLMUnavailableGraceful` - Offline LLM handling
- `TestInvalidInputHandling` - Invalid input validation
- `TestDocumentUploadErrors` - Upload error handling

**Run:**
```bash
uv run pytest tests/test_general/ -v
```

**Example Output:**
```
tests/test_general/test_system_checks.py::TestOllamaAvailability::test_ollama_service_running PASSED
tests/test_general/test_system_checks.py::TestOllamaAvailability::test_ollama_api_accessible PASSED
tests/test_general/test_error_handling.py::TestInvalidPDFHandling::test_corrupt_pdf_doesnt_crash PASSED
```

---

### test_api/ - API Endpoint Testing

**Purpose:** FastAPI endpoint validation and error handling

**Tests:**
- Root endpoint (/)
- Health check endpoint
- Document upload endpoint
- Chat query endpoint
- Error handling for invalid inputs

**Run:**
```bash
uv run pytest tests/test_api/ -v
```

**Status:** ✅ 5/5 passing

---

### test_criteria/ - Business Logic Validation

**Purpose:** K001-K006 criteria validation and citation accuracy

**Test Classes:**
- `TestCriteriaK001Validation` - Project information requirements
- `TestCriteriaK002Validation` - Applicant information requirements
- `TestCriteriaK003Validation` - Financial information requirements
- `TestCriteriaK004Validation` - Business plan requirements
- `TestCriteriaK005Validation` - Management team requirements
- `TestCriteriaK006Validation` - Sustainability plan requirements
- `TestMixedCriteriaResults` - Combined validation scenarios
- `TestCitationAccuracy` - Citation source verification

**Run:**
```bash
uv run pytest tests/test_criteria/ -v
uv run pytest tests/test_criteria/ -k "k001" -v
```

**Status:** ✅ 13/13 new tests

---

### test_integration/ - Multi-Component Workflows

**Purpose:** End-to-end testing of complete application flows

**Tests:**
- Dashboard page load
- Chat page load
- Document upload flow
- Chat query flow

**Run:**
```bash
uv run pytest tests/test_integration/ -v
```

**Status:** ⚠️ 2/4 passing (route integration issues)

**Known Issues:**
- `test_document_upload_flow` - Returns 404 (route path mismatch)
- `test_chat_query_flow` - Response format issue (missing citation fields)

**Fix Plan:**
1. Update route definitions in API
2. Update test mocking to match actual routes
3. Verify response format matches spec

---

### test_rag/ - RAG Pipeline Components

**Purpose:** Comprehensive testing of RAG (Retrieval-Augmented Generation) pipeline

**Submodules:**
- `test_chunker.py` - Document chunking logic
- `test_embeddings.py` - Embedding model and caching
- `test_end_to_end.py` - Complete RAG workflows
- `test_full_pipeline.py` - Pipeline orchestration
- `test_llm_chain.py` - LLM chain orchestration
- `test_llm_provider.py` - LLM provider connectivity
- `test_pipeline_integration.py` - Pipeline integration
- `test_prompts.py` - Prompt templating
- `test_real_world_chunking.py` - Real document chunking
- `test_vector_store.py` - Vector store operations

**Run:**
```bash
uv run pytest tests/test_rag/ -v
uv run pytest tests/test_rag/test_llm_chain.py -v
uv run pytest tests/test_rag/ -k "chunking" -v
```

**Status:** ✅ 60/60 passing (Excellent coverage)

---

### test_parsers/ - Document Parsing

**Purpose:** Document format parsing and validation

**Formats Tested:**
- PDF (`test_pdf_parser.py`) - 5 tests
- DOCX (`test_docx_parser.py`) - 5 tests
- XLSX (`test_xlsx_parser.py`) - 5 tests

**Run:**
```bash
uv run pytest tests/test_parsers/ -v
uv run pytest tests/test_parsers/test_pdf_parser.py -v
```

**Status:** ✅ 15/15 passing

**Coverage:**
- Parser initialization
- Format acceptance/rejection
- Missing file handling
- Invalid format handling
- Edge cases per format

---

### test_ollama/ - LLM Integration

**Purpose:** Ollama service integration testing

**Tests:**
- Infrastructure availability
- Model connectivity
- Response validation

**Run:**
```bash
uv run pytest tests/test_ollama/ -v
```

**Status:** ⚠️ 1/1 minimal test (placeholder)

**Expansion Opportunity:**
- Model loading tests
- Response parsing tests
- Timeout handling
- Error scenarios

---

### test_benchmarks/ - Performance Benchmarking

**Purpose:** Performance evaluation of multiple LLM models

**Models Tested:**
- `qwen2.5:0.5b` - Lightweight model (397 MB)
- `qwen2.5:7b` - Standard model (4.7 GB)
- `ministral-3:3b` - Mistral variant (3.0 GB)

**Benchmarks:**
- Model loading
- Hello world response
- Mathematical reasoning
- Logical reasoning

**Results Location:**
```
tests/test_benchmarks/results/run_2025-12-08_*.json
```

**Run:**
```bash
cd tests/test_benchmarks/
uv run python test_suite.py
```

**Documentation:**
- `PHASE_1_REPORT.md` - Initial implementation report
- `README.md` - Benchmark suite documentation
- `BENCHMARK_INTEGRATION_REPORT.md` - Integration findings

---

## Test Structure

### Directory Organization

```
tests/
├── __init__.py                    # Package marker
├── conftest.py                    # Pytest configuration & fixtures
│
├── test_general/                  # System health & error handling
│   ├── __init__.py
│   ├── test_system_checks.py     # Deployment readiness (11 tests)
│   └── test_error_handling.py    # Error scenarios (12+ tests)
│
├── test_api/                      # API endpoint testing
│   ├── __init__.py
│   └── test_endpoints.py         # FastAPI endpoints (5 tests)
│
├── test_criteria/                 # Business logic validation
│   ├── __init__.py
│   └── test_criteria_validation.py # K001-K006 (13 tests)
│
├── test_integration/              # Multi-component workflows
│   ├── __init__.py
│   └── test_full_workflow.py     # E2E workflows (4 tests)
│
├── test_rag/                      # RAG pipeline
│   ├── __init__.py
│   ├── test_chunker.py           # Chunking logic
│   ├── test_embeddings.py        # Embedding models
│   ├── test_end_to_end.py        # E2E workflows
│   ├── test_full_pipeline.py     # Pipeline orchestration
│   ├── test_llm_chain.py         # Chain orchestration
│   ├── test_llm_provider.py      # LLM connectivity
│   ├── test_pipeline_integration.py
│   ├── test_prompts.py           # Prompt templates
│   ├── test_real_world_chunking.py
│   └── test_vector_store.py      # Vector store ops
│
├── test_parsers/                  # Document parsing
│   ├── __init__.py
│   ├── test_pdf_parser.py        # PDF parsing
│   ├── test_docx_parser.py       # DOCX parsing
│   └── test_xlsx_parser.py       # XLSX parsing
│
├── test_ollama/                   # LLM integration
│   ├── __init__.py
│   └── test_infrastructure.py    # Ollama connectivity
│
└── test_benchmarks/               # Performance benchmarking
    ├── __init__.py
    ├── test_suite.py             # Main orchestrator
    ├── PHASE_1_REPORT.md         # Implementation report
    ├── README.md                 # Benchmark documentation
    ├── BENCHMARK_INTEGRATION_REPORT.md
    │
    ├── config/
    │   └── models.toml           # Model configuration
    │
    ├── utils/
    │   ├── llm_client.py        # Ollama wrapper
    │   └── config.py            # Configuration loader
    │
    ├── tests/
    │   ├── test_01_loading.py
    │   ├── test_02_hello_world.py
    │   ├── test_03_math.py
    │   └── test_04_logic.py
    │
    └── results/
        └── run_2025-12-08_*.json # Benchmark results
```

### Naming Conventions

**Test File Names:**
- Prefix: `test_`
- Format: `test_<component>_<aspect>.py`
- Example: `test_pdf_parser.py`, `test_llm_chain.py`

**Test Class Names:**
- Prefix: `Test`
- Format: `Test<ComponentName>`
- Example: `TestPDFParser`, `TestLLMChain`, `TestCriteriaK001Validation`

**Test Method Names:**
- Prefix: `test_`
- Format: `test_<what_is_tested>_<expected_outcome>`
- Example: `test_pdf_parsing_returns_text`, `test_corrupt_pdf_raises_error`

**Fixture Names:**
- Lowercase with underscores
- Descriptive: `mock_llm`, `test_client`, `temp_project`

---

## Writing New Tests

### Basic Test Template

```python
"""Tests for [component/feature]."""

import pytest
from unittest.mock import MagicMock, patch


class TestComponentFeature:
    """Test [component/feature] behavior."""

    def test_happy_path_scenario(self):
        """Verify [component] works correctly with valid input."""
        # Arrange
        input_data = {"key": "value"}
        expected_output = "expected"
        
        # Act
        result = function_under_test(input_data)
        
        # Assert
        assert result == expected_output

    def test_error_handling(self):
        """Verify [component] handles errors gracefully."""
        # Arrange
        invalid_input = None
        
        # Act & Assert
        with pytest.raises(ValueError, match="description"):
            function_under_test(invalid_input)

    def test_with_mock(self):
        """Verify [component] calls dependency correctly."""
        # Arrange
        mock_dep = MagicMock()
        mock_dep.method.return_value = "mocked_value"
        
        # Act
        result = ComponentClass(dependency=mock_dep).call_method()
        
        # Assert
        assert result == "mocked_value"
        mock_dep.method.assert_called_once()


# Pytest markers
pytestmark = [pytest.mark.unit]
```

### Adding Tests for New Features

1. **Identify test category:**
   - API endpoint? → `test_api/`
   - RAG pipeline? → `test_rag/`
   - Document parsing? → `test_parsers/`
   - Business logic? → `test_criteria/`
   - Error scenario? → `test_general/`

2. **Create test file** (if new file needed):
   - Follow naming convention: `test_<component>.py`
   - Add `__init__.py` if creating new subdirectory

3. **Write test class:**
   - One class per component/feature
   - Group related tests together
   - Use descriptive docstrings

4. **Run and verify:**
   ```bash
   uv run pytest tests/<category>/test_<component>.py -v
   ```

5. **Add to documentation:**
   - Update this file if adding new test category
   - Document purpose and usage

### Best Practices

**DO:**
- ✅ Test one thing per test method
- ✅ Use descriptive test names (avoid `test_1`, `test_2`)
- ✅ Use fixtures for shared setup
- ✅ Mock external dependencies (LLM, DB, API calls)
- ✅ Test both success and failure paths
- ✅ Add clear docstrings explaining what's tested
- ✅ Use parametrize for testing multiple inputs
- ✅ Keep tests fast (mock slow operations)

**DON'T:**
- ❌ Test multiple things in one test
- ❌ Create interdependent tests
- ❌ Use hardcoded data paths
- ❌ Test implementation details, test behavior
- ❌ Skip cleanup (use fixtures/teardown)
- ❌ Test external services directly (mock them)
- ❌ Ignore test failures

### Testing Patterns

**Pattern 1: Mocking LLM Calls**
```python
@patch('backend.llm.ollama_client.call_model')
def test_with_mocked_llm(self, mock_llm):
    mock_llm.return_value = "Model response"
    result = function_using_llm()
    assert "response" in result
```

**Pattern 2: Testing with Parametrize**
```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiple_inputs(input, expected):
    assert function(input) == expected
```

**Pattern 3: Testing Errors**
```python
def test_invalid_input_raises_error(self):
    with pytest.raises(ValueError, match="Invalid"):
        function(None)
```

**Pattern 4: Using Fixtures**
```python
@pytest.fixture
def mock_client(self):
    return MagicMock()

def test_with_fixture(self, mock_client):
    mock_client.call.return_value = "result"
    assert function(mock_client) == "result"
```

---

## Fixtures and Helpers

### conftest.py - Shared Configuration

**Location:** `tests/conftest.py`

**Current Status:** Minimal, ready for expansion

**Available Fixtures (Templates for future):**

```python
@pytest.fixture
def test_client():
    """FastAPI test client."""
    # Returns client for API testing

@pytest.fixture
def mock_llm():
    """Mocked LLM client."""
    # Returns mock that doesn't hit Ollama

@pytest.fixture
def temp_project(tmp_path):
    """Temporary project directory."""
    # Returns path to temporary project
```

### Using Fixtures in Tests

```python
def test_with_fixture(test_client):
    """Example test using fixture."""
    response = test_client.get("/health")
    assert response.status_code == 200
```

### Creating Custom Fixtures

```python
# In conftest.py
@pytest.fixture
def sample_document():
    """Fixture providing sample document."""
    return {
        "id": "doc-1",
        "content": "Sample document text",
        "format": "pdf"
    }

# In test file
def test_with_sample(sample_document):
    result = parse_document(sample_document)
    assert result is not None
```

---

## Troubleshooting

### Common Issues

**Issue: Tests pass locally but fail in CI**
- Solution: Ensure dependencies are installed (`uv sync --all-extras`)
- Solution: Check environment variables (API keys, paths)
- Solution: Verify database connectivity

**Issue: "No such file or directory" in tests**
- Solution: Use absolute paths or pytest fixtures for paths
- Solution: Don't assume working directory
```python
# Bad
with open("tests/data/file.txt") as f:

# Good
import pytest
from pathlib import Path
data_dir = Path(__file__).parent / "data"
```

**Issue: Tests timeout**
- Solution: Increase pytest timeout: `pytest --timeout=300`
- Solution: Mock slow operations instead of calling them
- Solution: Check if services (Ollama, DB) are running

**Issue: Mock not working**
- Solution: Import from correct location (where it's used, not where it's defined)
- Solution: Verify mock is applied before function is called
```python
# Correct
@patch('backend.module.function')  # Where it's used
def test_func(mock):
    pass

# Incorrect
@patch('other_module.function')  # Where it's defined
def test_func(mock):
    pass
```

**Issue: "Pytest.mark.integration not registered"**
- Solution: Add to `pyproject.toml`:
```toml
[tool.pytest.ini_options]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests",
]
```

**Issue: Database/Ollama connection failures**
- Solution: Check if services running:
```bash
ollama list
ps aux | grep ollama
ps aux | grep chroma
```
- Solution: Reset state between tests with fixtures
- Solution: Use mocks instead of real services

### Debugging Tips

**Run single test with output:**
```bash
uv run pytest tests/test_api/test_endpoints.py::test_root_endpoint -vv -s
```

**Show print statements:**
```bash
uv run pytest tests/ -s
```

**Get traceback info:**
```bash
uv run pytest tests/ --tb=long
```

**Run in Python debugger:**
```bash
uv run pytest tests/ --pdb
# Type 'c' to continue, 'n' for next, 's' for step into
```

**Generate coverage for single file:**
```bash
uv run pytest tests/ --cov=src.backend.api --cov-report=term-missing
```

---

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    
    - name: Install dependencies
      run: |
        pip install uv
        uv sync --all-extras
    
    - name: Run tests
      run: uv run pytest tests/ --ignore=tests/test_benchmarks -v
    
    - name: Generate coverage
      run: uv run pytest tests/ --cov=src --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
```

### Pre-commit Hook

```bash
# .githooks/pre-commit
#!/bin/bash
uv run pytest tests/ --ignore=tests/test_benchmarks -q
if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi
```

### Minimum Passing Criteria

- **Total Pass Rate:** ≥ 95% (excluding benchmarks)
- **API Tests:** 100% passing
- **RAG Tests:** 100% passing
- **Parser Tests:** 100% passing
- **Code Coverage:** ≥ 80%
- **Critical Paths:** 100% covered

---

## Coverage Reports

### Generate Coverage Report

```bash
uv run pytest tests/ --ignore=tests/test_benchmarks \
  --cov=src \
  --cov-report=html \
  --cov-report=term-missing
```

### View HTML Report

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

### Coverage by Module

```bash
# Coverage for specific module
uv run pytest tests/ --cov=src.backend.api --cov-report=term-missing

# Coverage for multiple modules
uv run pytest tests/ --cov=src.backend.api --cov=src.backend.rag --cov-report=term-missing
```

### Coverage Thresholds

Set minimum coverage in `pyproject.toml`:

```toml
[tool.coverage.run]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
]
fail_under = 80
```

---

## Test Execution Workflow

### Complete Test Session

```bash
# 1. Install dependencies
uv sync --all-extras

# 2. Verify services running
ollama list

# 3. Run quick tests
uv run pytest tests/test_general/ -v

# 4. Run full suite
uv run pytest tests/ --ignore=tests/test_benchmarks -v

# 5. Generate coverage
uv run pytest tests/ --cov=src --cov-report=html

# 6. Review coverage
open htmlcov/index.html

# 7. Run benchmarks (optional, takes longer)
cd tests/test_benchmarks/
uv run python test_suite.py
```

### After Making Code Changes

```bash
# Quick validation (only changed component)
uv run pytest tests/test_api/ -v

# Full validation (all tests)
uv run pytest tests/ --ignore=tests/test_benchmarks -v

# With coverage
uv run pytest tests/ --cov=src --cov-report=term-missing
```

---

## Performance Notes

### Test Execution Times

- **test_general/** - ~5-10 seconds (depends on system health)
- **test_api/** - ~2-3 seconds (mocked endpoints)
- **test_criteria/** - <1 second (unit tests)
- **test_integration/** - ~10-20 seconds (slower, more I/O)
- **test_rag/** - ~30-60 seconds (embedding model loading)
- **test_parsers/** - ~5-10 seconds (document parsing)
- **test_ollama/** - ~2-3 seconds (minimal)
- **TOTAL** - ~60-120 seconds (full suite)

### Optimization Tips

- Use `--timeout=300` to abort hanging tests
- Mock slow operations (Ollama, embeddings)
- Run tests in parallel: `pytest-xdist` plugin
- Use `-x` flag to stop on first failure

---

## Summary

This guide provides everything needed to understand, run, and extend the test suite. Key points:

1. **Run tests regularly** - catch issues early
2. **Mock external services** - keep tests fast
3. **Write descriptive tests** - future maintainers will thank you
4. **Maintain coverage** - aim for >80%
5. **Document changes** - update this guide when adding new tests

For questions or issues, refer to the troubleshooting section or check test output for clues.

---

**Last Updated:** December 8, 2025  
**Test Suite Version:** 2.0  
**Status:** Comprehensive coverage with 121+ tests across 8 categories
