# Backend Core
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 2.0 (⚠️ OPTION 2+ ONLY - NOT APPLICABLE TO OPTION 1)  
**Stand:** 8. November 2025

---

## ⚠️ WICHTIG: DIESES DOKUMENT IST FÜR OPTION 2+ ⚠️

**Option 1 (MVP) verwendet:**
- ✅ Streamlit UI (kein FastAPI)
- ✅ Einfache Python-Funktionen (keine REST API)
- ✅ Lokales Filesystem (kein Redis Queue)
- ✅ Direkter LM Studio Call (keine Service-Layer)

**Dieses Dokument beschreibt die Enterprise-Architektur für Option 2+**

---

## Übersicht - ⚠️ OPTION 2+

Backend-System für die Antragsprüfung mit FastAPI und Microservices.

## Architektur - ⚠️ OPTION 2+

### Komponenten
- API-Server (FastAPI)
- LLM-Service
- Storage-Service
- Task-Queue (Redis)

### Tech-Stack
- Python 3.11+
- FastAPI
- Redis Queue
- PostgreSQL/SQLite

## Services - ⚠️ OPTION 2+

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

## Datenmodelle - ⚠️ OPTION 2+

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

## Error-Handling - ⚠️ OPTION 2+

### Strategien
- Retry-Mechanismen
- Fallback-Optionen
- Structured Logging

### Monitoring
- Service-Health
- Performance Metrics
- Fehlerquoten

## Deployment - ⚠️ OPTION 2+

### Docker Setup
- Multi-Container
- Env-Konfiguration
- Logging-Setup