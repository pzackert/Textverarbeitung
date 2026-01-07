# CHANGES & API USAGE

## 1. Änderungsprotokoll
### 1.1 Neu implementierte Features
- Persistenz der Kriterienscans in data/input/{project_id}/criteria_responses.json inklusive Summary, Evidence und Zeitstempeln ([src/services/criteria_results_store.py](src/services/criteria_results_store.py)).
- Erweiterte Validierung speichert Evidenzen, normalisiert Status (grün/gelb/rot), misst Laufzeit und schreibt in criteria_responses.json ([src/services/validation_service.py](src/services/validation_service.py)).
- Neue Ergebnis-Endpoints und Bulk-Evaluation mit Background-Job-Tracking ([src/api/routers/criteria.py](src/api/routers/criteria.py#L41-L210)).
- Dokumentliste liefert has_annotated-Flag, annotierte Metadaten, Seitenzahl, Timestamps, Criteria-Verwendung ([src/api/routers/projects.py](src/api/routers/projects.py#L24-L170)).
- Tests für Bulk-Evaluation und Annotated-Zugriff ([tmp/test_bulk_evaluation.py](tmp/test_bulk_evaluation.py), [tmp/test_annotated_access.py](tmp/test_annotated_access.py)).

### 1.2 Geänderte Endpoints
- GET /projects/{project_id}/documents liefert jetzt Rich-Metadaten inkl. has_annotated & used_in_criteria.
- GET /projects/{project_id}/criteria/results, /summary, /{criterion_id}/result neu.
- POST /projects/{project_id}/criteria/evaluate-all + GET /projects/{project_id}/criteria/evaluate-all/{job_id}/status neu.
- Einzel-Evaluation POST /projects/{project_id}/criteria/{criterion_id}/evaluate schreibt jetzt Persistenz & Timing.

## 2. System-Management APIs
- **Healthcheck**
  - Zweck: Status von API + LLM + Storage prüfen.
  - Endpoint: GET /api/system/health ([src/api/routers/system.py](src/api/routers/system.py#L15-L62))
  - Response: `{ "status": "healthy|degraded", "components": {"llm": {...}, "rag": {...}, "storage": {...}} }`
- **Startup**
  - Zweck: Startup-Sequence triggern (idempotent).
  - Endpoint: POST /api/system/startup
  - Response: `{ "message": "Startup initiated", "status": "initializing|ready" }`
- **Status**
  - Zweck: Detaillierter Systemstatus.
  - Endpoint: GET /api/system/status
  - Response: `SystemStatus` Model (siehe system_state).

## 3. RAG-Management APIs
- **Global Load**
  - Zweck: Global Knowledge (data/global_knowledge) neu indizieren.
  - Endpoint: POST /api/rag/global/load ([src/api/routers/rag_global.py](src/api/routers/rag_global.py#L53-L96))
  - Response: `{ job_id, status:"started", total_documents, documents:[...] }`
- **Global Status**
  - Endpoint: GET /api/rag/global/status ([src/api/routers/rag_global.py](src/api/routers/rag_global.py#L99-L104))
  - Response: `rag_job` inkl. documents[], progress_pct, total_chunks.
- **Global Unload**
  - Endpoint: POST /api/rag/global/unload ([src/api/routers/rag_global.py](src/api/routers/rag_global.py#L107-L121))
  - Response: `{ status:"unloaded", chunks_removed, duration_sec }`
- **Project Ingest**
  - Zweck: Projekt-Dokumente in Vektor-Store laden.
  - Endpoint: POST /projects/{project_id}/rag/ingest ([src/api/routers/projects.py](src/api/routers/projects.py#L200-L260))
  - Response: `{ status:"success", ingested_count }`
- **Project Unload**
  - Zweck: Projekt-spezifische Chunks entfernen.
  - Endpoint: POST /api/rag/project/{project_id}/unload ([src/api/routers/rag_project.py](src/api/routers/rag_project.py#L9-L32))
  - Response: `{ status:"unloaded", project_id }`

## 4. Chat-Management APIs
- **Global Chat erstellen**
  - Endpoint: POST /api/chats/global/create
  - Response: `{ chat_id, created_at, file_path, type:"global" }`
- **Global Chat Message**
  - Endpoint: POST /api/chats/global/{chat_id}/message
  - Body: `{ "message": "...", "include_rag": true|false }`
  - Response: `{ chat_id, message_id, user_message, assistant_message }`
- **Project Chat Message**
  - Endpoint: POST /api/chats/project/{project_id}/message
  - Body: `{ "message": "...", "include_rag": true }`
  - Response analog global.
- **Project Chat History**
  - Endpoint: GET /api/chats/project/{project_id}
  - Response: `{ project_id, messages:[...] }`

## 5. Dokument-Management APIs
- **Dokumentliste**
  - Endpoint: GET /projects/{project_id}/documents ([src/api/routers/projects.py](src/api/routers/projects.py#L83-L170))
  - Zweck: Frontend-Übersicht mit Annotierungsstatus.
  - Response-Beispiel:
    ```json
    {
      "documents": [
        {
          "filename": "projektantrag.pdf",
          "path": "/uploads/projektantrag.pdf",
          "size_mb": 2.3,
          "pages": 15,
          "uploaded_at": "2025-12-15T10:00:00Z",
          "has_annotated": true,
          "annotated_file": "projektantrag_annotated.pdf",
          "annotated_path": "/annotated/projektantrag_annotated.pdf",
          "annotated_at": "2025-12-19T14:30:15Z",
          "used_in_criteria": ["K001", "K003"]
        }
      ],
      "total": 2
    }
    ```
- **Annotierte Dateien auflisten**
  - Endpoint: GET /projects/{project_id}/documents/annotated
  - Response: `AnnotatedListResponse` inkl. criteria, highlights_count.
- **Annotierte Datei herunterladen**
  - Endpoint: GET /projects/{project_id}/documents/annotated/{filename}
  - Response: File download (pdf/docx/xlsx/json).
- **PDF Highlights lesen**
  - Endpoint: GET /projects/{project_id}/documents/annotated/{filename}/highlights
  - Response: `{ document, highlights:[{page, bbox, text, criterion_id}] }`
- **Compare Original vs Annotated**
  - Endpoint: GET /projects/{project_id}/documents/compare?original=...&annotated=...
  - Response: Größe, Seitenzahl, download_url, highlights_count.

## 6. Kriterien-Management APIs
- **Kriterien CRUD**
  - Endpoints: GET/POST/PUT/DELETE /criteria (siehe [src/api/routers/criteria.py](src/api/routers/criteria.py#L10-L62)).
- **Einzel-Evaluation**
  - Endpoint: POST /projects/{project_id}/criteria/{criterion_id}/evaluate
  - Zweck: Ein Kriterium bewerten, annotieren, persistieren.
  - Response: `{ criterion_id, status:"grün|gelb|rot", score, reason, annotations:[...], annotated_file, evaluated_at, evidence:[...] }`
- **Bulk-Evaluation**
  - Endpoint: POST /projects/{project_id}/criteria/evaluate-all
  - Body (optional): `{ "criteria_ids": ["K001",...], "overwrite": true }` (overwrite aktuell nicht verwendet)
  - Response: `{ job_id, status:"started", total_criteria, criteria_ids }`
  - Status-Polling: GET /projects/{project_id}/criteria/evaluate-all/{job_id}/status → liefert progress.results[], summary, estimated_remaining_sec.
- **Persistierte Ergebnisse abrufen**
  - Full: GET /projects/{project_id}/criteria/results → komplette criteria_responses.json
  - Summary: GET /projects/{project_id}/criteria/results/summary → nur summary
  - Einzelnes Kriterium: GET /projects/{project_id}/criteria/{criterion_id}/result
- **Annotations je Kriterium**
  - Endpoint: GET /projects/{project_id}/criteria/{criterion_id}/annotations → aktuelle project.validation_results (in-memory) mit annotations[].

## 7. Frontend Use Cases → API Mapping
- **Dashboard Health**: GET /api/system/health to show system status.
- **Global Knowledge Reload**: POST /api/rag/global/load then poll GET /api/rag/global/status until `status:"ready"`.
- **Projekt-Ingest**: POST /projects/{project_id}/rag/ingest, danach Chat/RAG nutzbar.
- **Dokumentenliste anzeigen**: GET /projects/{project_id}/documents → render has_annotated Badge, enable download links.
- **Annotierte Highlights anzeigen**: GET /projects/{project_id}/documents/annotated/{file}/highlights → visuelles Overlay im PDF-Viewer.
- **Kriterium bewerten (Einzel)**: POST /projects/{project_id}/criteria/{criterion_id}/evaluate → nach Abschluss GET /projects/{project_id}/criteria/{criterion_id}/result für persistierte Daten.
- **Alle Kriterien bewerten**: POST /projects/{project_id}/criteria/evaluate-all → Poll Status → Nach Abschluss GET /projects/{project_id}/criteria/results für Anzeige/Export.
- **Summary Widgets**: GET /projects/{project_id}/criteria/results/summary → Zahlen für evaluated/pending und Status-Counts.

## Datenfluss (High-Level)
- Evaluation ruft validation_service → annotation_service → schreibt Annotate-Files nach data/input/{project_id}/annotated und Evidence nach criteria_responses.json ([src/services/validation_service.py](src/services/validation_service.py#L15-L150)).
- criteria_results_store erstellt/updated criteria_responses.json und Summary ([src/services/criteria_results_store.py](src/services/criteria_results_store.py#L1-L120)).
- Dokumentliste liest uploads + criteria_responses.json, korreliert Evidence → used_in_criteria ([src/api/routers/projects.py](src/api/routers/projects.py#L83-L170)).
- Bulk-Evaluation hält Job-Status in-memory (evaluation_jobs) für Polling ([src/api/routers/criteria.py](src/api/routers/criteria.py#L120-L210)).
