# LLM Chain Usage Guide

## Overview

The `LLMChain` is the core component of the RAG system, orchestrating the flow from user query to final answer. It integrates retrieval, prompt engineering, LLM generation, and response parsing.

## Components

1.  **RetrievalEngine**: Fetches relevant document chunks.
2.  **PromptBuilder**: Constructs context-aware prompts (German).
3.  **LLMProvider**: Connects to Ollama (or other providers).
4.  **ResponseParser**: Extracts citations and structures the output.

## Usage

### Basic Initialization

Use the factory function to create a fully configured chain:

```python
from src.rag.llm_chain import create_llm_chain

# Initialize from config/config.yaml
chain = create_llm_chain()
```

### Running Queries

#### Simple Query (Text Only)
```python
answer = chain.query_with_context("Wer ist antragsberechtigt?")
print(answer)
```

#### Detailed Query (With Metadata)
```python
result = chain.query("Wer ist antragsberechtigt?")

print(f"Answer: {result['answer']}")
print(f"Duration: {result['metadata']['duration']}s")

# Access Citations
for citation in result['citations']:
    print(f"Source: {citation['source']}, Page: {citation['page']}")
```

### Template Types

The `query` method supports different prompt templates:

-   `"standard"` (Default): General Q&A.
-   `"evaluation"`: For checking specific criteria (returns structured assessment).
-   `"summary"`: For summarizing retrieved content.

```python
# Evaluation Example
result = chain.query(
    "Unternehmen muss Sitz in Hamburg haben", 
    template_type="evaluation"
)
```

## Error Handling

The chain handles common errors gracefully:

-   **No Documents Found**: Returns a polite message instead of crashing.
-   **LLM Unavailable**: Raises `ConnectionError` (should be caught by UI).
-   **Parsing Errors**: Returns raw text if citation parsing fails.

## Configuration

Settings in `config/config.yaml`:

```yaml
rag:
  llm_provider: "ollama"
  llm_model: "qwen2.5:7b"
  llm_base_url: "http://localhost:11434"
  llm_temperature: 0.7
  llm_max_tokens: 2000
```

## Best Practices

1.  **Check Availability**: Always check `chain.llm_provider.is_available()` before starting a session.
2.  **Handle Latency**: LLM generation can take seconds. Show a spinner in the UI.
3.  **Use Citations**: Always display the sources returned in `result['citations']` to build trust.
