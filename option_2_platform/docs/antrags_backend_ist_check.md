# Ist-Zustand Antragsverarbeitung (Backend)

## 1) Projekt-/Datenhaltung
- Projekte werden aus `data/input/registry.json` geladen (`project_service`). Ohne Eintrag in registry existiert das Projekt im Backend nicht, auch wenn der Ordner vorhanden ist.
- Dokumente werden beim `get_project` dynamisch aus `data/input/<id>/uploads/` eingelesen; Metadaten (name, applicant, status, validation_results etc.) bleiben in registry.json, nicht in einem projektlokalen `metadata.json`.
- Chat-Historien liegen projektlokal in `data/input/<id>/chat_history.json`.
- Kriterien-Resultate liegen in `data/input/<id>/criteria_responses.json` (nicht `criteria_results/`-Ordner, keine pro-Kriterium-Dateien).
- Annotierte Dateien liegen in `data/input/<id>/annotated/`; Uploads in `uploads/`. Sonstige Struktur (metadata.json, criteria_results/, chat_history.json) ist aktuell nicht implementiert.

## 2) Relevante Endpunkte (Review-Cockpit)
- Projekt-Dokumente: `GET /api/projects/{id}/documents` (liest uploads, zeigt annotated-Verknüpfungen, Seitenzahl bei PDF, Criteria-Usage aus criteria_responses.json).
- Dateien: `GET /api/projects/{id}/documents/uploads/{file}`, `GET /api/projects/{id}/documents/annotated/{file}`, Highlights `GET /api/projects/{id}/documents/annotated/{file}/highlights`.
- Annotated-Liste: `GET /api/projects/{id}/documents/annotated` (zählt Highlights, ordnet Criteria zu).
- Vergleich: `GET /api/projects/{id}/documents/compare?original=...&annotated=...`.
- RAG: `POST /api/rag/project/{id}/ingest` (pipeline für alle Dokumente), `POST /api/projects/{id}/documents/{doc_id}/ingest`, `DELETE /api/projects/{id}/rag` (löscht Chunks nach project_id-Metadaten).
- Chat (Projekt): `GET /api/chats/project/{id}`, `POST /api/chats/project/{id}/message` (nutzt LLMChain mit metadata_filter={project_id: ...}). Chat-Dateien jedoch in `data/chats/`, nicht im Projektordner.
- Kriterien: `POST /api/projects/{id}/criteria/{criterion_id}/evaluate` (ruft validation_service), Ergebnisse nach criteria_responses.json.

## 3) Kriterien-Evaluierung (validation_service)
- Kriterienbasis: `config/criteria_catalog.json` via `criteria_service`.
- Aktuelle Logik: rein regelbasiert/heuristisch für Hamburg-PLZ (PDF/DOCX/XLSX/TXT). Kein LLM, keine sequenzielle Abarbeitung aller Kriterien, keine Queue.
- Annotierungen: `annotation_service.annotate_document` erzeugt annotated Files (PDF/DOCX/XLSX oder .txt.meta.json) im Projekt-`annotated/`-Ordner; evidences werden in criteria_responses.json gespeichert.
- Ergebnisse werden zusätzlich in `project.validation_results` (im registry-Objekt) abgelegt.

## 4) Projektstruktur vs. Zielbild
- Sollbild laut Wunsch: pro Projektordner `uploads/`, `annotated/`, `metadata.json`, `criteria_results/`, `chat_history.json`.
- Ist: registry.json als zentrale Datenbasis, criteria_responses.json als Sammeldatei, chat_history bereits projektlokal `chat_history.json`, kein metadata.json, kein criteria_results/-Ordner.
- Konsequenz: Ohne registry-Eintrag ist ein neuer Ordner nicht sichtbar; Löschung/Umbenennung des Ordners spiegelt sich nicht automatisch in registry.json.

## 5) Frontend-Anbindung (laut Ist-Doku)
- Übersicht: `GET /api/projects` (liefert registry-basierte Projekte); Detail: `GET /api/projects/{id}/documents`, Chat, Criteria, Annotated-Calls wie oben.
- Viewer zeigt Original/Annotiert über die genannten Endpunkte; Ingest wird beim Seitenladen getriggert.
- Kriterien-Overlay nutzt criteria_catalog.json + criteria_responses.json; manuelle Bestätigungen sind im JS angedeutet, aber Persistenz-Endpunkt fehlt.

## 6) Offene Risiken / Gaps
- Abhängigkeit von registry.json kollidiert mit Wunsch "Ordner = Wahrheit". Kein automatisches Scannen aller `data/input/*`-Ordner als Projekte.
- Fehlende projektlokale Metadaten: `metadata.json` wird weder gelesen noch geschrieben.
- Kriterien-Persistenz: alles in einer Datei `criteria_responses.json`; kein Ordner je Kriterium; keine Historie/Versionierung; keine Queue für Re-Evaluierung bei neuen Kriterien.
- Chat-Ablage nicht projektspezifisch im Ordner.
- Kriterien-Evaluierung nutzt keine LLM/RAG-Analyse; nur Hamburg-PLZ-Heuristik → inhaltliche Abdeckung stark begrenzt.
- Annotierungen: evidences werden gespeichert, aber Mapping zu Kriterien in Dateien erfolgt über criteria_responses.json; kein Abgleich gegen Soll-Struktur.

## 7) Was aktuell geht (Backend)
- Dateien pro Projekt aus `uploads/` werden gelistet und serviert; annotierte Dateien werden gelistet/serviert; Highlights für PDFs können extrahiert werden.
- RAG-Ingest kann für Projekt-Dokumente angestoßen werden; Chunks können nach project_id gelöscht werden.
- Projekt-Chat mit RAG-Filter project_id ist vorhanden (Storage jedoch in `data/chats/`).
- Einzelkriterium-Evaluierung erzeugt Annotierungen + evidences und speichert in criteria_responses.json.

## 8) Was nicht dem Zielbild entspricht
- Kein automatisches Projekt-Discovery über Ordnerstruktur; registry.json als Gate.
- Keine `metadata.json`-Nutzung; keine `criteria_results/`-Folder-Struktur; keine `chat_history.json` im Projektordner.
- Keine LLM-basierte Kriterienprüfung; keine sequenzielle/Queue-basierte Neubewertung bei neuen Kriterien.
- Frontend-Checkbox/Bestätigung für Kriterien scheint kein Backend-Speicherpfad zu haben.

## 9) Empfohlene Klärungen/Nächste Schritte (ohne Umsetzung)
- Entscheiden: Registry.json beibehalten oder durch Folder-Scan ersetzen? Wenn Scan, wie werden Metadaten (Name, Antragsteller, Status) gepflegt? → metadata.json pro Projekt?
- Ablage-Design festziehen: chat_history.json, criteria_results/ pro Kriterium oder Sammeldatei? Versionierung nötig?
- Kriterien-Engine: Soll künftig LLM/RAG prüfen? Dann Ingestion/Chunking und Prompting-Flow definieren (inkl. Queue bei neuen Kriterien).
- Frontend-Persistenz für manuelle Kriteriumsbestätigung definieren (Endpoint + Speicherort).
- Backlog: Adapter bauen, der bestehende registry.json + criteria_responses.json in das Ziel-Filesystem migriert.
