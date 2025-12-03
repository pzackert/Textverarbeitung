# Parser Integration Strategy

## 1. Input Interface
The RAG system receives data from the Phase 2 Parsers via the `Document` model.

```python
# From Phase 2
@dataclass
class Document:
    content: str
    metadata: Dict[str, Any]
```

## 2. Ingestion Workflow
1.  **Load**: `Parser.parse(file_path)` -> Returns `Document`.
2.  **Validate**: Check if `Document.content` is not empty.
3.  **Chunk**: Pass `Document` to `Chunker.split(document)`.
4.  **Embed & Store**: Pass chunks to `VectorStore.add(chunks)`.

## 3. Metadata Mapping
The Parser metadata must be mapped to ChromaDB metadata (flat dict).

| Parser Metadata | ChromaDB Metadata | Handling |
|-----------------|-------------------|----------|
| `filename` | `source` | Direct copy |
| `file_type` | `doc_type` | Direct copy |
| `page_count` | `total_pages` | Direct copy |
| `creation_date` | `created_at` | Convert to ISO string |
| `author` | `author` | Direct copy |

## 4. Error Propagation
- **Parser Error**: If a file fails to parse, log the error and skip the file. Do not halt the entire batch ingestion.
- **Empty Content**: If a file parses but has no text (e.g., scanned PDF without OCR), log a warning "Skipping empty document: {filename}".

## 5. Testing Integration
- Create a test script `scripts/test_ingestion.py` that:
    1.  Iterates over `option_1_mvp/data/input/`.
    2.  Parses each file.
    3.  Ingests into a *temporary* ChromaDB collection.
    4.  Verifies count of chunks in DB.
