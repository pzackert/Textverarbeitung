# Backend Core
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 8. November 2025

## Übersicht

Backend-System für die Antragsprüfung.

## Architektur

### Komponenten
- API-Server
- LLM-Service
- Storage-Service
- Task-Queue

### Tech-Stack
- Python 3.11+
- FastAPI
- Redis Queue
- SQLite/JSON

## Services

### API-Service
- REST-Endpunkte
- Authentifizierung
- Rate-Limiting

### Storage-Service
- Dokumenten-Management
- Metadaten-Verwaltung
- Caching

### Processing-Service
- Dokumenten-Verarbeitung
- LLM-Integration
- Ergebnis-Handling

## Datenmodelle

### Projekt
```python
class Project:
    id: str
    name: str
    created_at: datetime
    status: ProjectStatus
    documents: List[Document]
    results: List[Result]
```

### Dokument
```python
class Document:
    id: str
    project_id: str
    filename: str
    type: DocumentType
    status: ProcessingStatus
    metadata: Dict
```

## Error-Handling

### Strategien
- Retry-Mechanismen
- Fallback-Optionen
- Logging

### Monitoring
- Service-Health
- Performance
- Fehlerquoten

## Deployment

### Lokal
- Docker-Setup
- Env-Konfiguration
- Logging-Setup