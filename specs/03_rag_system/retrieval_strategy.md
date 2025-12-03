# Retrieval Strategy

## 1. Query Processing
Before a user query is sent to the vector store, it undergoes preprocessing:
1.  **Cleaning**: Remove excessive whitespace and special characters that might distort meaning.
2.  **Expansion (Optional)**: Add synonyms or related terms (Future feature).
3.  **Embedding**: Convert query text to vector using the *same* model as ingestion (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`).

## 2. Similarity Search
- **Metric**: Cosine Similarity.
- **Top-K**: Retrieve top `k` results (Configurable, default `k=5`).
- **Threshold**: Discard results with similarity score < `threshold` (Configurable, default `0.7`).

## 3. Ranking & Filtering
1.  **Primary Sort**: By Similarity Score (Descending).
2.  **Metadata Filtering**:
    - If user specifies a document context (e.g., "In Document A..."), apply metadata filter `where={"source": "Document A"}`.
3.  **Deduplication**: If multiple chunks from the exact same section are returned (due to overlap), keep only the highest scoring one or merge them.

## 4. Context Assembly
Constructing the context window for the LLM:
1.  **Format**:
    ```text
    Source: {filename} (Page {page})
    Content: {chunk_text}
    ---
    Source: {filename} (Page {page})
    Content: {chunk_text}
    ```
2.  **Token Limit**: Ensure total context tokens + prompt tokens < Model Context Window (e.g., 4096 or 8192).
3.  **Truncation**: If `Top-K` chunks exceed the limit, drop the lowest-scoring chunks until it fits.

## 5. Fallback Strategies
- **No Results**: If no chunks meet the threshold -> Return "No relevant information found in the provided documents."
- **Low Confidence**: If top score is between 0.5 and 0.7 -> Add disclaimer "Note: The following information might be only partially relevant."
