# Frontend Handover – Backend Stand (Jan 2026)

Ziel: Nur Frontend-Anpassungen/Tests, keine weiteren Backend-Logik-Changes. Fokus auf Bedienbarkeit der neuen/angepassten APIs.

## Wichtige Backend-Änderungen (seit letztem Commit)
- Startup & Global Knowledge
  - Global Knowledge wird nun im Hintergrund geladen (kein Blockieren des Startups). Status weiterhin unter `/api/system/status`.
  - Neue Settings-/Status-Flows: `model_scanner`, `ai_provider`, `vector_store`, `llm_loading`, `global_knowledge`, `project_healing` im Status-Response.
- API-Router-Erweiterungen
  - Settings-Endpunkte hinzugefügt (Modell-/Provider-Konfiguration): `/api/settings/*`.
  - Queue-Router für Kriterien-Pipeline: `/api/queue/...` (Projekt-spezifisch), Polling-fähig.
- Chat & RAG
  - Global Chat: `/api/chats/global/create` (nutzt global knowledge; Seeds aus config/prompts).
  - Projekt-Chat: `/api/chats/project/{project_id}/message` erzwingt Quellen; `project_id` muss aus Ordnerstruktur kommen.
  - RAG-Projekt-Endpunkte: `/api/rag/project/{project_id}/ingest|status|unload` mit strikter Isolierung.
- Projekt-Discovery
  - Keine `registry.json` mehr. Projekte werden aus `data/input/<project_id>/` erkannt und bei Bedarf ge-healt (uploads/, annotated/, metadata.json, criteria_responses.json, chat_history.json).
- Parser & Ingestion
  - CSV-Support hinzugefügt (tabellarische Blöcke). Erlaubte Extensions: pdf, docx, xlsx, csv, txt.
  - Fallback PyMuPDF bei Docling-Miss-Ergebnissen.
- Hyperparameter/Config
  - `config/config.yaml`: max_tokens 16000, chunk_size 1200, overlap 100, top_k 8, similarity_threshold 0.90.

## Erwartete Frontend-Anpassungen
- Status-Anzeige
  - `/api/system/status` liefert neue Komponentenliste; Frontend sollte „ready“ und Komponenten-Progress lesen.
- Settings-UI
  - Modelle/Provider: `/api/settings/models`, `/api/settings/llm`, `/api/settings/rag`, `/api/settings/prompts` (Restart-Info beachten falls im UI angezeigt).
- Chat
  - Global Chat: POST `/api/chats/global/create` (Option: `include_global=true` default). UI muss diesen Endpoint nutzen; alter Pfad ggf. anpassen.
  - Projekt-Chat: POST `/api/chats/project/{id}/message` (Quellenpflicht; Fehlermeldung 503, wenn keine Quellen).
- RAG & Ingestion
  - Projekt-Ingest: POST `/api/rag/project/{id}/ingest` (Uploads aus `data/input/<id>/uploads/`). Status-Polling `/api/rag/project/{id}/status`.
  - Global Knowledge wird automatisch geladen; kein UI-Trigger nötig. (Optional: Status-Anzeige möglich.)
- Queue/Kriterien
  - Enqueue/Poll unter `/api/queue/projects/{id}/criteria/all` und `/api/queue`. Falls UI Polling implementiert, Pfade prüfen.
- Projekt-Liste
  - Projekte rein über Ordner; API gibt alle `data/input/*` zurück. Frontend darf nicht mehr auf registry.json vertrauen.

## Tests, die der Frontendler ausführen soll
1) System-Status: GET `/api/system/status` → Status `ready` und Komponenten sichtbar.
2) Global Chat: POST `/api/chats/global/create` → Antwort mit Quellen aus global knowledge.
3) Projekt-Chat: POST `/api/chats/project/{demo_id}/message` → Antwort mit Quellen, keine 503, wenn Projekt-Daten vorhanden.
4) Projekt-Ingest: POST `/api/rag/project/{demo_id}/ingest` → Status-Polling, danach Chat mit Projektdaten.
5) Settings: GET `/api/settings/models` + POST `/api/settings/llm` (Hello-World) → 200er.
6) Queue: Enqueue/Poll für Projekt → Status aktualisiert.

## Known Gaps / Zu prüfen im Frontend
- Global Chat Pfad sicherstellen (`/api/chats/global/create`).
- Neue Status-Komponenten im Dashboard anzeigen.
- Settings-Views an neue `/api/settings/*` Pfade koppeln.
- Projekt-Liste nicht mehr aus registry, sondern aus `/api/projects` (Ordner-basiert).
- Polling für RAG/Queue korrekt (Status-Routen oben).

## Daten-/Pfad-Hinweise
- Global Knowledge liegt in `data/global_knowledge/` (Auto-Load im Hintergrund).
- Projekt-Daten: `data/input/<project_id>/uploads/` etc.
- Vectorstore: `data/chromadb/` (bereits git-ignored).

Bitte keine Backend-Logik ändern, nur Frontend anpassen/testen.
