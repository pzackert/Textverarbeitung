# RAG System
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 8. November 2025

## Übersicht

RAG (Retrieval-Augmented Generation) System für intelligente Dokumentenanalyse.

## Komponenten

### ChromaDB
- Vektordatenbank
- Collections pro Projekt
- Persistente Speicherung

### Chunking
- Intelligente Textsegmentierung
- Überlappende Chunks
- Strukturerhaltung

### Embeddings
- BAAI/bge-large-en-v1.5
- Batch-Processing
- Caching

## Prozessablauf

### 1. Indexierung (pro Projekt)
Nach dem Upload der 2 Dokumente:

1. **Projektskizze parsen**
   - Text extrahieren
   - In Chunks aufteilen (1000 Tokens, 200 Overlap)
   - Embeddings erstellen
   
2. **Projektantrag parsen**
   - Formular-Struktur erkennen
   - Abschnitte extrahieren
   - In Chunks aufteilen
   - Embeddings erstellen

3. **In ChromaDB speichern**
   - Collection: `projekt_{projekt_id}`
   - Alle Chunks mit Metadaten
   - Persistente Speicherung

### 2. Retrieval (pro Kriterium)
Bei der Prüfung jedes Kriteriums:

1. **Query erstellen** (aus Kriterium-Prompt)
2. **Query vektorisieren**
3. **Ähnlichkeitssuche** in ChromaDB
   - Top 5 relevante Chunks
   - Similarity Threshold: 0.75
4. **Kontext aufbauen** aus gefundenen Chunks
5. **An LLM übergeben** zusammen mit Kriterium-Prompt

## Datenhaltung

### Collection
- Ein Collection pro Projekt
- Metadata pro Chunk
- Versionierung

### Performance
- Batch-Verarbeitung
- Index-Optimierung
- Cache-Strategie

## Integration

### Input
- Parsed Documents
- Strukturierte Daten
- Metadaten

### Output
- Relevante Chunks
- Konfidenzwerte
- Strukturierte Antworten