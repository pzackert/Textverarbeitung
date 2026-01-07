# Technische Bestandsaufnahme: Antragsverarbeitung

## 1. Architektur-Übersicht
Die Antragsverarbeitung ("Review Cockpit") ist eine Single-Page-Application (SPA) innerhalb des Server-Side-Rendered (SSR) Rahmens.
*   **Backend**: FastAPI (`src/api/routers/projects.py`, `src/api/routers/chat_project.py`).
*   **Frontend**: Jinja2 Templates + Alpine.js + Vanilla JS (`static/js/review.js`, `static/js/chat.js`).
*   **State Management**: Globales `ReviewState` Objekt + Alpine.js Komponenten.

---

## 2. Komponenten-Detailanalyse

### 2.1 Dokumenten-Sidebar (Zone A)
*   **Template**: `project_review.html` (Lines 82-188).
*   **Logik**: `static/js/review.js`.
*   **Datenquelle**: `GET /api/projects/{projectId}/documents`.
*   **Verhalten**:
    *   Initialer Load: `loadProjectDocuments()` fetchet Metadaten.
    *   **RAG-Ingest**: Startet im Hintergrund via `POST /api/rag/project/{id}/ingest` beim Laden der Seite.
    *   **Polling**: `pollIngestionStatus()` prüft alle 2 Sekunden auf `ready`/`error` Status für jedes File und aktualisiert Icons.
*   **Event-Handling**:
    *   Klick auf File (`.file-item`): Ruft global `loadDocument(filename)` auf.
    *   Deep-Link Support: URL-Parameter `?doc=filename.pdf&page=5` werden beim Init ausgewertet.

### 2.2 Dokumenten-Viewer (Zone B)
*   **Template**: `components/document_viewer.html`.
*   **Core-Klasse**: `DocumentViewer` (`static/js/viewer/DocumentViewer.js`).
*   **Renderer**:
    *   `PdfRenderer` (basierend auf `pdf.js`): Unterstützt Highlighting via Coordinate-Mapping.
    *   `DocxRenderer` (mammoth.js): HTML-Konvertierung.
    *   `XlsxRenderer` (SheetJS): HTML-Table Rendering.
*   **Ansichts-Toggles**:
    *   `Original`: Lädt `/api/projects/{id}/documents/uploads/{file}`.
    *   `Annotiert`: Lädt `/api/projects/{id}/documents/annotated/{file}`.
    *   Logik: `window.toggleView(mode)` ruft `viewer.toggleView()`.

### 2.3 KI-Assistent & RAG (Zone C)
*   **Template**: `components/ai_assistant.html`.
*   **Logik**: `static/js/chat.js` (`ChatManager` Klasse).
*   **API-Endpunkt**: `POST /api/chats/project/{id}/message`.
*   **Payload**: `{ message: "...", include_rag: true }`.
*   **Antwort-Struktur (JSON)**:
    ```json
    {
      "assistant_message": {
        "content": "Antwort...",
        "sources": [
            { "doc_name": "Antrag.pdf", "page": 5, "snippet": "..." }
        ],
        "metrics": { "tokens_per_second": 45.2 }
      }
    }
    ```
*   **Quellen-Verlinkung**:
    *   Backend liefert `sources` Array.
    *   Frontend rendert Buttons: `window.renderDocument(docName)` -> Interner Call zu `loadDocument()`.
    *   Features: Klick springt direkt zur Seite (falls PDF).

### 2.4 Kriterienkatalog (Overlay)
*   **Template**: `partials/criteria_catalog.html` (dynamisch geladen oder embedded).
*   **Datenbasis**: `config/criteria_catalog.json` (Definitionen) + `data/projects/{id}/validation_results.json` (Ergebnisse).
*   **API**: `POST /api/projects/{id}/criteria/{criterionId}/evaluate`.
*   **Flow**:
    1.  User öffnet Katalog.
    2.  `fetchCriteriaResults()` lädt gespeicherten Status.
    3.  Manuelle Bewertung ("Bestätigen") sendet Update an Backend (fehlt im Code: Persistierung der manuellen Bestätigung scheint nur client-seitig visuell oder unvollständig implementiert in `review.js`).

---

## 3. Datenfluss & APIs

| Bereich | Methode | Endpoint | Zweck |
| :--- | :--- | :--- | :--- |
| **Meta** | `GET` | `/api/projects/{id}/documents` | Liste aller Dateien & Status. |
| **Content** | `GET` | `/api/projects/{id}/documents/uploads/{file}` | Raw File (Original). |
| **Content** | `GET` | `/api/projects/{id}/documents/annotated/{file}` | Raw File (Annotiert). |
| **RAG** | `POST` | `/api/rag/project/{id}/ingest` | Trigger Ingest pipeline. |
| **Chat** | `GET` | `/api/chats/project/{id}` | Lade Chat-Historie. |
| **Chat** | `POST` | `/api/chats/project/{id}/message` | Sende Nachricht an LLM. |
| **Criteria** | `POST` | `/api/projects/{id}/criteria/{mid}/evaluate` | Prüfe einzelnes Kriterium. |

## 4. Technische Schulden / Auffälligkeiten
*   **HTMX Mix**: Teilweise HTMX Attribute im Code (`hx-post`), die aber via JS (`e.stopImmediatePropagation`) unterdrückt werden. Migration zu reinem Alpine/JS scheint unvollständig.
*   **Fehlende Persistenz**: Manuelle Bestätigungen im Kriterienkatalog scheinen keinen Backend-Endpunkt zu haben, der den "Confirmed"-Status speichert.
*   **Polling**: RAG-Status wird via Polling gelöst; keine WebSockets.
