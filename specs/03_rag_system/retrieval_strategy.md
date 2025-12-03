# Retrieval Strategy

## 1. Query Processing
Bevor eine User-Query an den Vector Store geht:
1.  **Cleaning**: Entfernen von überflüssigen Whitespaces.
2.  **Expansion (Optional)**: Synonyme hinzufügen (Future Feature).
3.  **Embedding**: Umwandlung in Vektor mit *demselben* Modell wie Ingestion (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`).

## 2. Similarity Search
- **Metrik**: Cosine Similarity.
- **Top-K**: Abruf der Top `k` Ergebnisse (Konfigurierbar, Default `k=5`).
- **Threshold**: Verwerfen von Ergebnissen mit Score < `threshold` (Default `0.7`).

## 3. Ranking & Filtering
1.  **Primary Sort**: Nach Similarity Score (Absteigend).
2.  **Metadata Filtering**:
    - Wenn User Kontext spezifiziert (z.B. "In Dokument A..."), Filter `where={"source": "Dokument A"}` anwenden.
3.  **Deduplication**: Wenn mehrere Chunks aus demselben Abschnitt kommen, nur den besten behalten oder mergen.

## 4. Context Assembly
Zusammenbau des Kontext-Fensters für das LLM:
1.  **Format**:
    ```text
    Quelle: {filename} (Seite {page})
    Inhalt: {chunk_text}
    ---
    Quelle: {filename} (Seite {page})
    Inhalt: {chunk_text}
    ```
2.  **Token Limit**: Sicherstellen, dass Kontext + Prompt < Model Context Window (z.B. 4096).
3.  **Truncation**: Wenn `Top-K` Chunks das Limit sprengen, die schlechtesten verwerfen.

## 5. Fallback Strategien
- **Keine Ergebnisse**: Wenn kein Chunk den Threshold erreicht -> "Keine relevanten Informationen in den Dokumenten gefunden."
- **Niedrige Konfidenz**: Score zwischen 0.5 und 0.7 -> Hinweis "Informationen sind möglicherweise nur teilweise relevant."

