# Backend Übergabeprotokoll – Stand nach Umsetzung aller Backend-Phasen

## Technische Änderungen (Backend)
- Projekte sind ordnerbasiert (data/input/<id>) inkl. Healing für uploads/, annotated/, metadata.json, chat_history.json, criteria_responses.json.
- Dokumentenzählung basiert ausschließlich auf uploads/; Status/Metadaten in metadata.json; Summary der Kriterien wird nach jeder Auswertung in metadata.json gespiegelt.
- RAG-Isolation pro Projekt: delete_projects_except + delete_project vor jedem Ingest; Queue arbeitet FIFO und blockt Duplikate (pending/running) mit identischem project_id + criteria_ids.
- Kriterien-Engine nutzt criteria_catalog + prompts.kriterien_pruefung, JSON-Retry, Status-Normalisierung (rot/gelb/grün), Evidence/Annotation schreiben nach annotated/ und criteria_responses.json.
- Global Knowledge wird beim Start (außer pytest) automatisch geladen, wenn data/global_knowledge existiert und Dateien enthält; global chat prüft Verfügbarkeit (im Testmodus gebypasst).
- Global/Projekt-Chat seedet Handshake (global_chat_initial + begruessung); Projekt-Chat erzwingt Quellen, sonst 503; Chat-Verläufe: global unter data/chats/, projektbezogen unter data/input/<id>/chat_history.json.
- APIs: Queue (/api/queue...), Projekt-RAG (/api/rag/project/{id}/ingest/status/unload), Global-RAG (/api/rag/global/load/status/unload), Chat global (/api/chats/global...), Chat projekt (/api/chats/project/{id}/...).

## Erwartete Frontend-Anpassungen
- Projektlisten/Details: Status & Dokumentenzahl aus metadata.json + uploads; Kriterien-Summary aus metadata.json.criteria_summary.
- Queue-UX: Duplikate visualisieren (Job-Antwort enthält duplicate=true bei gleicher criteria_ids & project_id, Status pending/running).
- RAG-Statusanzeige: global_rag_status aus /api/rag/global/status; projekt_rag_status aus /api/rag/project/{id}/status; globale Knowledge-Fehler (503) als Blocker für global chat anzeigen.
- Chat: Handshake-Messages sind bereits vorhanden; Projektchat-Antworten liefern sources mit document/doc_name; Fehler 503 aus Projektchat bei fehlender RAG klar kommunizieren.
- Kriterien-Resultate: lesen aus criteria_responses.json (API-Response) oder metadata.json.criteria_summary; Evidence/annotated_file aus Backend-Response anzeigen.

## Prompts/Runtime-Hinweise für FE-Dev
- Nutzung Backend-API (Base: /api):
  - Projekte laden: GET /api/projects
  - Projekt-Dokumente: GET /api/projects/{id}/documents
  - Projekt-RAG-Status: GET /api/rag/project/{id}/status; start: POST /api/rag/project/{id}/ingest
  - Global-RAG-Status: GET /api/rag/global/status; start: POST /api/rag/global/load
  - Queue: POST /api/queue/projects/{id}/criteria/all (oder single), Status: GET /api/queue
  - Global Chat: POST /api/chats/global/create -> chat_id, dann POST /api/chats/global/{chat_id}/message
  - Projekt Chat: GET/POST /api/chats/project/{id}[/message]

## Arbeits-Prompt für FE-Developer (konkret ausführen)
1) Nutze obige Endpunkte gegen das laufende Backend (Base /api). Stelle sicher, dass global knowledge geladen ist (POST /api/rag/global/load) oder zeige Blocker an.
2) Implementiere Status-Badges: global_rag_status, projekt_rag_status, queue_job_status (pending/running/done/failed/duplicate).
3) Binde Kriterien-Summary (metadata.json.criteria_summary) in Projektübersicht ein; dokumentiere uploads-count und status.
4) Chat-Flows: global und projekt, nutze bereits gesendete Seed-Messages, zeige Quellen (document) an, handle 503-Fehler als Info-Toast.
5) Für Queue: nach Enqueue Polling /api/queue, zeige Fortschritt pro criterion_id; markiere duplicate=true Jobs als Hinweis statt erneut zu starten.
6) Teste mit aktuellen Endpunkten; keine Frontend-Änderungen an Backend-Struktur vornehmen.

---

# Frontend Requirements & Umsetzungsplan

## WICHTIG: Optische Vorgaben
**Keine Design-Änderungen!** Alle UI-Elemente (Tabellen, Badges, Sidebar, Chat-Bubbles) müssen optisch 1:1 erhalten bleiben. Wir ersetzen lediglich "Dummy-Daten" durch echte API-Calls.

## Phase 1: Projekt-Übersicht (`/projects`)
**Ziel:** Korrekte Anzeige der Projektliste basierend auf der neuen Backend-Logic.

### 1.1 Datenanbindung
*   **Source:** `GET /api/projects`
*   **Columns Mapping:**
    *   `Antragsnummer`: `project.id`
    *   `Projektname`: `project.name`
    *   `Antragsteller`: `project.applicant`
    *   `Fördersumme`: `project.funding_amount` (formatiert)
    *   `Status`: `project.status` (Mapping auf Badges: 'Entwurf' (grau), 'Inprüfung' (gelb), 'Abgeschlossen' (grün))
    *   `Dokumente`: `project.documents_count` (Nur Uploads, nicht annotated!)
    *   `Letzte Änderung`: `project.last_updated`

### 1.2 Queue-Integration in Übersicht (Optional für Phase 1, Pflicht für Phase 2)
*   **Button "Kriterien prüfen"**:
    *   Sollte in der Actions-Spalte verfügbar sein (ggf. als Dropdown-Option).
    *   **Action:** `POST /api/queue/projects/{id}/criteria/all`.
    *   **Feedback:** Toast "Prüfung gestartet" + Optisches Feedback am Status-Badge (z.B. kleiner Spinner).

## Phase 2: Review-Cockpit & RAG (`/projects/{id}/review`)
**Ziel:** Sicherstellen, dass die Datenbasis (RAG) korrekt geladen ist, bevor gearbeitet wird.

### 2.1 RAG-Steuerung
*   **Beim Laden der Seite:** Check `GET /api/rag/project/{id}/status`.
*   **Logic:**
    *   Status `ready`: Alles grün. Chat & Kriterien freigeben.
    *   Status `indexing`/`loading`: Spinner anzeigen, Inputs disablen. Polling alle 2s.
    *   Status `error`/`not_indexed`:
        *   Automatisch `POST /api/rag/project/{id}/ingest` triggern.
        *   Toast/Banner anzeigen: "Projektdaten werden analysiert...".

### 2.2 Dokumentenliste
*   **Source:** `GET /api/projects/{id}/documents`
*   **Anzeige:**
    *   Liste der Dateien (wie bisher in Sidebar).
    *   Klick lädt Datei im Viewer (existierende Logic beibehalten).
    *   RAG-Status Icons pro Datei (falls API dies liefert, sonst Projekt-Status nutzen).

## Phase 3: Kriterien-Queue & Overlay
**Ziel:** Asynchrone Prüfung ohne UI-Blocker.

### 3.1 Overlay Daten
*   **Source:** `GET /api/projects/{id}/criteria/results` (oder ähnlicher Endpoint, der `criteria_responses.json` liefert).
*   **Darstellung:**
    *   Items: Wie bisher (K001, K002...)
    *   Status: Checkbox/Badge basierend auf JSON-Ergebnis (`status: "grün"|"rot"`).
    *   Evidence: Wenn JSON `evidence`-Feld hat, Link zum Dokument anzeigen.

### 3.2 Prüfung Starten (Queue)
*   **Action:** Button "Alle prüfen" oder Einzel-Button.
*   **API:** `POST /api/queue/projects/{id}/criteria/{critId}`.
*   **Duplicate Handling:**
    *   Wenn API `duplicate=true` zurückgibt: Toast "Prüfung läuft bereits".
*   **Polling:**
    *   Globales oder lokales Polling von `GET /api/queue`.
    *   Filter auf `project_id`.
    *   Update der Status-Icons im Overlay live (Pending -> Running -> Done).

## Phase 4: Chat-Flows & Fehlerbehandlung
**Ziel:** Robuster Chat mit Quellen und Fehler-Feedback.

### 4.1 Global Chat
*   **API:** `POST /api/chats/global/...`
*   **Init:** Keine Begrüßung senden (kommt vom Backend).
*   **Fehler 503:** Wenn Backend "Global Knowledge missing" meldet -> Roter Banner im Chat "Wissensbasis fehlt. Bitte System prüfen." (Admin-Aufgabe, oder Button "Laden" falls User-Recht).

### 4.2 Projekt Chat
*   **API:** `POST /api/chats/project/{id}/message`
*   **Payload:** `{ "message": "...", "include_rag": true }`
*   **Sources:**
    *   Backend liefert `sources: [{ "document": "...", "page": 1 }]`.
    *   **Frontend Action:** Rendere diese als kleine Chips unter der Antwort.
    *   **Click:** Muss `loadDocument(docName, page)` aufrufen (Deep Linking).
*   **Fehler 503:** Wenn "RAG nicht bereit" -> Toast "Bitte warten, Dokumente werden noch verarbeitet".

---

## Qualitäts-Checkliste für Umsetzung
- [ ] **Optik:** Kein Pixel verschoben? (Vergleich mit Screenshots)
- [ ] **RAG-Gate:** Chat funktioniert erst, wenn RAG `ready` ist?
- [ ] **Queue:** UI blockiert nicht während der Prüfung?
- [ ] **Progress:** User sieht, dass etwas passiert (Spinner/Toast)?
- [ ] **Sources:** Klick auf Quelle öffnet korrekte PDF-Seite?
- [ ] **Error:** Backend-Fehler werden als lesbare Toasts angezeigt?
