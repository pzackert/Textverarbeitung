# Parser Integration Strategy

## 1. Input Interface
Das RAG System empfängt Daten von den Phase 2 Parsern via `Document` Model.

```python
# Aus Phase 2 (src/parsers/models.py)
@dataclass
class Document:
    content: str
    metadata: Dict[str, Any]
```

## 2. Ingestion Workflow
1.  **Load**: `Parser.parse(file_path)` -> Liefert `Document`.
2.  **Validate**: Prüfen ob `Document.content` nicht leer ist.
3.  **Chunk**: `Document` an `Chunker.split(document)` übergeben.
4.  **Embed & Store**: Chunks an `VectorStore.add(chunks)` übergeben.

## 3. Metadata Mapping
Parser-Metadaten müssen auf ChromaDB-Metadaten (flaches Dict) gemappt werden.

| Parser Metadata | ChromaDB Metadata | Handling |
|-----------------|-------------------|----------|
| `filename` | `source` | 1:1 Kopie |
| `file_type` | `doc_type` | 1:1 Kopie |
| `page_count` | `total_pages` | 1:1 Kopie |
| `creation_date` | `created_at` | Konvertierung zu ISO String |
| `author` | `author` | 1:1 Kopie |

## 4. Error Propagation
- **Parser Error**: Loggen und Datei überspringen. Batch-Prozess läuft weiter.
- **Empty Content**: Warnung loggen "Skipping empty document: {filename}".

## 5. Testing Integration
- Test-Skript `scripts/test_ingestion.py` erstellen:
    1.  Iteriert über `option_1_mvp/data/input/`.
    2.  Parst jede Datei.
    3.  Ingestiert in *temporäre* ChromaDB Collection.
    4.  Verifiziert Chunk-Anzahl.

