# Testing Strategy

## Automated Tests

Run the test suite using `uv`:

```bash
uv run pytest
```

### Key Test Areas
-   `tests/api/`: Endpoint availability and response schemas.
-   `tests/rag/`: Response parser logic (regex for citations) and config loading.
-   `tests/services/`: File system operations (create, delete, scan).

## Manual End-to-End Validation

1.  **Fresh Install**: Delete `data/input` and `data/chromadb`. Restart server. Verify auto-creation of folders.
2.  **Upload Flow**: Create a project, upload a PDF. Verify it appears in Sidebar.
3.  **RAG Flow**: Ingest document. Ask "What is this document?". Verify answer + citation.
4.  **Criteria Flow**: Run a check (e.g., K001). Verify status changes from Pending -> Loading -> Success/Fail.
5.  **Restart**: Trigger restart via UI. Verify system comes back up without error.

## Benchmarking

To test local LLM performance:
1.  Check the logs during generation.
2.  Chat responses include metrics:
    -   **Tokens per second**: Should be > 10 for good UX.
    -   **Time to First Token (TTFT)**: Should be < 2 seconds.
3.  Adjust `chunk_size` or `chunk_overlap` in settings if retrieval is too slow.
