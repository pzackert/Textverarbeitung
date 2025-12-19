# LLM Benchmark Suite - Phase 1

A production-ready benchmark system for evaluating LLM models across standardized tests with comprehensive metrics collection.

## Quick Start

### Run Benchmarks
```bash
cd /path/to/option_2_platform
uv run python tests/benchmarks/test_suite.py
```

### View Results
```bash
# Latest results
cat tests/benchmarks/results/run_*.json | jq '.'

# All runs
ls -lh tests/benchmarks/results/
```

## Architecture

### Core Components

1. **`test_suite.py`** - Main orchestrator
   - Loads configuration
   - Runs tests sequentially per model
   - Collects metrics
   - Saves JSON output

2. **`utils/config.py`** - Configuration loader
   - Parses TOML config files
   - Validates models and hyperparameters
   - Provides easy access to settings

3. **`utils/llm_client.py`** - LLM wrapper
   - Unified Ollama interface
   - Metrics collection (time, tokens/sec, RAM, CPU)
   - Model availability checking
   - Error handling and logging

4. **`tests/test_*.py`** - Individual tests
   - Test 1: Model Loading (warm-up time, RAM)
   - Test 2: Hello World (greeting validation)
   - Test 3: Math Reasoning (arithmetic)
   - Test 4: Logic Puzzle (reasoning)

### Configuration (`config/models.toml`)

```toml
[run]
repetitions = 3          # Repeat each test 3 times
warmup = true            # Warm up models before testing

[hyperparameters]
temperature = [0.0, 0.7, 1.0]      # Temperature variations
context_length = [2048, 4096, 8192] # Context length variations

[[models]]
name = "qwen2.5:7b"
backend = "ollama"
enabled = true
```

## Test Details

### Test 1: Model Loading
- **Purpose:** Measure loading time and resource usage
- **Metrics:** warmup_time_s, ram_used_mb
- **Pass Criteria:** Model responds successfully

### Test 2: Hello World
- **Purpose:** Baseline responsiveness test
- **Metrics:** response_time_s, tokens_per_sec
- **Pass Criteria:** Response contains "hello" or "hi"
- **Repetitions:** 3 attempts, averages computed

### Test 3: Math Reasoning
- **Purpose:** Test arithmetic capability
- **Prompt:** "Calculate: 4 + 8 × 7. Only give the number."
- **Expected Answer:** "60"
- **Metrics:** response_time_s, accuracy
- **Repetitions:** 3 attempts

### Test 4: Logic Puzzle
- **Purpose:** Test reasoning capability
- **Prompt:** "Three apples cost 6 euros. How much does one cost?"
- **Expected Answer:** Contains "2"
- **Metrics:** response_time_s, accuracy
- **Repetitions:** 3 attempts

## Results Format

JSON output with complete metadata:

```json
{
  "run_metadata": {
    "timestamp": "2025-12-08T10:19:02.879539Z",
    "system": {
      "os": "Darwin",
      "cpu_count": 8,
      "total_ram_gb": 16.0
    },
    "config": {
      "repetitions": 3,
      "warmup": true
    }
  },
  "results": [
    {
      "model": "qwen2.5:7b",
      "test": "01_model_loading",
      "passed": true,
      "warmup_time_s": 7.42,
      "ram_used_mb": 18.9
    },
    {
      "model": "qwen2.5:7b",
      "test": "02_hello_world",
      "passed": true,
      "attempts": [
        {
          "response_time_s": 0.85,
          "tokens_per_sec": 12.9,
          "answer": "Hello there!..."
        }
      ],
      "avg_response_time_s": 0.65,
      "avg_tokens_per_sec": 17.5
    }
  ]
}
```

## Extending the System

### Add a New Test

1. Create `tests/benchmarks/tests/test_05_your_test.py`
2. Use pytest parametrization for models
3. Use `LLMClient` to query models
4. Implement validation logic
5. Store metrics in result dict

### Add More Models

Edit `tests/benchmarks/config/models.toml`:

```toml
[[models]]
name = "neural-chat:7b"
backend = "ollama"
enabled = true
```

### Change Hyperparameters

Edit `[hyperparameters]` in `models.toml`:

```toml
[hyperparameters]
temperature = [0.0, 0.5, 1.0]
context_length = [1024, 2048, 4096]
```

## Metrics Collected

| Metric | Description | Unit |
|--------|-------------|------|
| `response_time_s` | Time to generate response | seconds |
| `tokens_per_sec` | Generation speed | tokens/second |
| `ram_used_mb` | Memory usage | megabytes |
| `cpu_percent` | CPU utilization | percentage |
| `warmup_time_s` | Model loading time | seconds |
| `accuracy` | Fraction of correct answers | 0.0-1.0 |

## Requirements

- Python 3.11+
- Ollama running on localhost:11434
- UV package manager
- psutil (for metrics)

## Project Structure

```
tests/benchmarks/
├── test_suite.py           # Main orchestrator
├── tests/
│   ├── test_01_loading.py
│   ├── test_02_hello.py
│   ├── test_03_math.py
│   └── test_04_logic.py
├── utils/
│   ├── config.py           # Config loader
│   └── llm_client.py       # LLM wrapper
├── config/
│   └── models.toml         # Configuration
└── results/
    └── run_*.json          # Result files
```

## Troubleshooting

### "Model not available"
- Ensure Ollama is running: `ollama serve`
- Check model is installed: `ollama list`
- Update `models.toml` with correct model names

### "Connection refused"
- Check Ollama is running on localhost:11434
- Verify firewall settings

### Slow tests
- Reduce `context_length` in config
- Reduce `repetitions`
- Close other applications

## Next Steps (Phase 2)

- [ ] Hyperparameter sweep across all combinations
- [ ] Parallel test execution
- [ ] Results visualization dashboard
- [ ] Statistical significance testing
- [ ] Performance regression detection
- [ ] Cost analysis per test

## References

- See `PHASE_1_REPORT.md` for detailed analysis
- See individual test files for implementation details
- Ollama docs: https://github.com/ollama/ollama

---

*Phase 1 Complete | Ready for Phase 2*
