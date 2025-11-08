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

### 1. Indexierung
1. Text chunken
2. Embeddings erstellen
3. In ChromaDB speichern

### 2. Retrieval
1. Query vectorisieren
2. Ähnlichkeit suchen
3. Kontext aufbauen
4. An LLM übergeben

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