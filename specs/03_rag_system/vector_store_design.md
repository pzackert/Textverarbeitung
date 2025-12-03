# Vector Store Design (ChromaDB)

## 1. ChromaDB Setup
- **Persistence**: Lokaler Speicher in `data/chromadb/`.
- **Client**: `chromadb.PersistentClient`.
- **Collection Name**: `ifb_documents`.
- **Distance Function**: `cosine` (Standard) oder `l2`.

## 2. Embedding Strategy
- **Library**: `sentence-transformers` (via `SentenceTransformerEmbeddingFunction`).
- **Modell**: `paraphrase-multilingual-MiniLM-L12-v2`
    - **Grund**: Starke Performance auf Deutsch, leichtgewichtig, lokal.
    - **Dimensionen**: 384.
    - **Max Sequence Length**: 128/256 Tokens.
- **Fallback**: `all-MiniLM-L6-v2` (falls multilingual nicht ausreicht).

## 3. Metadata Schema
Jeder Vektor in ChromaDB muss folgende Metadaten haben:

| Feld | Typ | Beschreibung | Beispiel |
|------|-----|--------------|----------|
| `source` | string | Dateiname | `Richtlinie_2024.pdf` |
| `page` | int | Seitennummer | `12` |
| `chunk_id` | int | ID des Chunks | `4` |
| `doc_type` | string | Dateityp | `pdf` |
| `created_at` | string | ISO Timestamp | `2025-12-03T10:00:00` |
| `category` | string | (Optional) Kategorie | `Richtlinie` |

## 4. Collection-Strategie
- **Single Collection**: `ifb_documents` für alle Dokumente.
- **Filterung**: Queries filtern bei Bedarf nach `source` oder `doc_type`.
- **Updates**:
    - **Add**: Embeddings berechnen -> Zur Collection hinzufügen.
    - **Update**: Löschen via `source` -> Neu ingestieren.
    - **Delete**: Löschen via `source`.

## 5. Performance Erwartungen
- **Datenbank Größe**: < 1GB für typischen Projektumfang.
- **Query Latenz**: < 50ms für Retrieval.
- **Embedding Generation**: < 100ms pro Chunk (CPU).
