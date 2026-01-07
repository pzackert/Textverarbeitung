# Backend Requirements – Antragsübersicht & Kriterien-Queue

## Projektphasen (End-to-End)
- Phase 1 – Requirements & Success Criteria
  - Abgleich aller Spezifikationen (dieses Dokument, config.yaml Prompts, criteria_catalog.json).
  - Definition der Akzeptanzkriterien pro Projekt 8209d44a und 14435678 (Startup-Healing, Queue, Chat, RAG-Isolation, JSON-Strictness, Evidence).
  - Offene Fragen/Annahmen dokumentieren; Test-Ziele festlegen (Funktions- und E2E-Scope).

- Phase 2 – Project Discovery & Healing
  - data/input als alleinige Quelle: Scan aller Unterordner; keine registry.json-Abhaengigkeit.
  - Auto-Healing: uploads/, annotated/, metadata.json, criteria_responses.json, chat_history.json anlegen/ersetzen bei Fehlen/Korruption.
  - Idempotenz: wiederholter Startup-Scan bleibt stabil; versteckte Ordner ignorieren.
  - Default-Felder (Status Entwurf, Timestamps) konsistent; Dokumentenzaehlung nur uploads/.

- Phase 3 – RAG Isolation & Lifecycle
  - Pro Job nur Chunks des Zielprojekts im VectorStore; Loeschung per project_id-Filter.
  - Reload der Projekt-Uploads vor jedem Job; Global/Regelwerke separat und persistent.
  - Schutz vor Stale-Indices (bestehende Fremd-Chunks entfernen, leere Sammlungen melden).
  - Timeouts/Fehlerpfade mit klaren Fehlermeldungen; Wiederverwendung bereits geladener Projekt-RAGs moeglich, wenn sauber.
  - Implementiert: delete_projects_except + delete_project im VectorStore; Queue- und RAG-Endpoints loeschen Fremd-Chunks vor Re-Ingest, Global-Knowledge bleibt erhalten.

- Phase 4 – Criteria Queue & Evaluation
  - Endpunkte: single criterion, all criteria per project, all criteria for all projects; FIFO Worker; Status-Polling.
  - Pro Job: RAG-Setup (Phase 3), Prompt-Kombination kriterien_pruefung + Katalog-Prompt, LLM-Call, JSON-Validierung mit Retry.
  - Persistenz in criteria_responses.json inkl. summary/Counts, Timestamps, evaluator, duration.
  - Evidence/Annotations schreiben; Fehlermodi (Katalog fehlt, RAG fehlt, Persistenzfehler) als failed Job mit Message.
  - Implementiert: Queue lädt Projekt-RAG isoliert (delete_projects_except + delete_project) vor jedem Job; Validation-Service erzwingt JSON-Parsing, Normalisierung (status rot/gelb/grün), Begründungstrunkierung (≤160 Zeichen), Retry bei Parse-Fehlern.

- Phase 5 – Chat Handshake & Policies
  - Global Chat: Handshake-Seed mit global_chat_initial + begruessung, antwort_richtlinie wird pro Turn mitgegeben; RAG muss geladen sein.
  - Projekt-Chat: nutzt Projekt-RAG (Phase 3) + Global-Knowledge; gleicher Handshake-Seed/Policy; Quellenpflicht (Datei + Referenz, sonst 400).
  - Fehlerpfade: fehlende RAG/Uploads → klare Fehlermeldung; defekte chat_history.json → Neuinitialisierung.

- Phase 6 – Storage, Evidence, Annotations
  - criteria_responses.json: konsistente Struktur (summary, criteria_results, last_evaluation), Crash-Sicherheit (temp write + replace).
  - Evidence enthaelt dokument, referenz, text_snippet; Annotationen nach annotated/ mit Suffix _annotated.ext; fehlende Positionsdaten werden toleriert.
  - chat_history.json Format fix; metadata.json Updates fuer Status/updated_at.

- Phase 7 – Testing & Fixtures
  - Unit/Integration: Startup-Scan-Healing, Dokumentenzaehlung, Status-API, Queue-Enqueue/Run, JSON-Strictness, Evidence/Annotation-Fallbacks.
  - E2E/Functional: Chat-Handshakes (global/projekt), RAG-Isolation pro Job, Duplicate-Queue-Submit, Katalog-Fehler, Persistenzfehler.
  - Fixtures: Projekte 8209d44a, 14435678 mit bereinigten annotated/; Helper zum Reset vor Tests.

- Phase 8 – End-to-End & Docs
  - Vollstaendige Pytest-Suite + gezielte E2E gegen 8209d44a/14435678; Logs erfassen.
  - Ergebnisdokumentation: bekannte Risiken, offene Punkte, Troubleshooting, Runbook fuer Queue/RAG/Chat.
  - README/Doc-Updates: neue Flows, Annahmen, Prompts, Limits.

## Phase 1 – Requirements & Success Criteria (Detail)
- Basisquellen
  - config/config.yaml: Prompts (begruessung, global_chat_initial, antrags_chat_initial, antwort_richtlinie, kriterien_pruefung), RAG-Settings, startup-Flags (auto_load_rag=true, fallback_to_ollama=true).
  - config/criteria_catalog.json: 17 Kriterien (K001–K016, K_TEST_AUTO) mit Prompt-Texten und Kategorien.
  - Datenbasis: data/input/{project_id}/uploads als einzige verbindliche Quelldokumente; globale Regelwerke unter data/regelwerke (falls verwendet); VectorStore unter data/chromadb.

- Akzeptanzkriterien (gesamt)
  - Prompts: kriterien_pruefung erzwingt JSON mit status/begruendung/dokument/referenz; antwort_richtlinie wird bei jedem Chat-Turn angewendet; global_chat_initial + begruessung bilden Handshake.
  - Projekte: werden ausschließlich durch Ordnerscan unter data/input erkannt; fehlende Mindestdateien werden erstellt (uploads/, annotated/, metadata.json, criteria_responses.json, chat_history.json).
  - RAG: Globale Wissensbasis bleibt geladen; pro Projekt-Jobs wird der VectorStore auf project_id gefiltert und mit uploads neu geladen; keine Fremd-Chunks im Kontext.
  - Queue: Enqueue-Endpunkte vorhanden (single/all/all-projects), FIFO-Verarbeitung, Status-Polling liefert pending/running/done/failed mit Message.
  - Kriterien-Resultate: responses in criteria_responses.json validieren das JSON-Schema (status ∈ {rot, gelb, gruen|grün}, begruendung ≤ 160 Zeichen, dokument/refenz null oder String); Evidence listet Quelle + Referenz; Annotate, falls Positionen vorhanden.
  - Chat: Global und Projektchat speichern Verlaeufe; Handshake-Fehler oder fehlender RAG führen zu klaren Fehlermeldungen; Projektchat-Antworten enthalten Quellen (Datei+Referenz).

- Projektspezifische Akzeptanzkriterien
  - Projekt 8209d44a
    - Startup-Healing legt fehlendes metadata.json an und normalisiert criteria_responses.json-Format (summary/criteria_results). Bestehende uploads/ bleiben unangetastet, annotated/ bleibt erhalten oder wird erstellt.
    - Queue-Lauf "all criteria" erzeugt fuer alle 17 Kriterien valide JSON-Ergebnisse; RAG nutzt nur uploads/8209d44a; Statusverteilung kann variieren, darf aber keine leeren/ungültigen Antworten enthalten.
    - Chat (Projekt) nach Handshake antwortet mit Quellenangaben (Dateiname + Referenz) aus den Projekt-Uploads; bei fehlendem RAG klare Fehlermeldung.
  - Projekt 14435678
    - Startup-Healing legt fehlendes metadata.json an; criteria_responses.json wird validiert/normalisiert.
    - Queue-Lauf "all criteria" erzeugt fuer alle 17 Kriterien valide JSON-Ergebnisse aus uploads/14435678; keine Fremd-Chunks im Kontext.
    - Chat (Projekt) Handshake und Antworten wie oben; bei fehlenden Uploads Fehlerhinweis.

- Test-Scope Phase 1 (Definition)
  - Statisch: config.yaml laden (Prompts vorhanden, JSON-Strictness in kriterien_pruefung), criteria_catalog.json parst und enthaelt IDs/Pflichtfelder; Projekte werden per Ordnerscan gelistet.
  - Dynamisch (Smoke):
    - Startup-Healing erzeugt Mindestdateien fuer 8209d44a und 14435678 (metadata.json, criteria_responses.json, chat_history.json, annotated/ falls fehlend).
    - RAG-Reset pro Job entfernt Fremd-Chunks vor Ingestion (delete_by_metadata project_id!=current).
    - Queue: enqueuen all-criteria fuer beide Projekte, Polling liefert done/failed mit Messages; criteria_responses.json enthaelt 17 Ergebnisse je Projekt, JSON-konform.
    - Chat: Global-Handshake gibt exakt begruessung zurueck; Projektchat-Handschlag laedt Projekt-RAG und erzwingt antwort_richtlinie, Antworten enthalten Quellen.
  - Datenbereinigung: Vor Runs annotated/ leeren (nur fuer Tests), RAG-Store fuer Fremd-Chunks pruefen und entfernen, defekte JSONs durch Defaults ersetzen.

## Ziele
- Ordnerstruktur unter `data/input` ist Single Source of Truth (keine registry.json als Gate).
- Robuste Initialisierung: fehlende Mindestdateien/Ordner automatisch anlegen.
- Einheitliche Projekt-Statuswerte: `Entwurf`, `Inprüfung`, `Abgeschlossen`.
- Dokumentzählung nur auf Basis `uploads/` (eingereichte Originale).
- Asynchrone Kriterien-Queue: mehrere Projekte/Kriterien einreihen, Zustand abrufbar.

## Systemstart & Komponenten-Health
- Startreihenfolge: Engine → Provider → LLM → RAG → Webservice. Jeder Schritt meldet ok/fail, Frontend kann Komponentenstatus abfragen.
- Global Knowledge wird beim Start in den RAG geladen: Pfad `data/global_knowledge` (bleibt im VectorStore verfügbar, kein Chat nötig).
- Fehlertoleranz: fehlender Global-Knowledge-Ordner oder leere Sammlung führt zu klarer Fehlermeldung und verhindert Chat-/Kriterien-Aufrufe, bis behoben.
- Auto-Healing wie beschrieben (Ordner/JSONs) läuft nach Komponenten-Start, bevor API Anfragen beantwortet.

## Projekt- und Datenmodell (Dateisystem)
- Jedes Projekt hat Ordner `data/input/<project_id>/` mit Mindeststruktur:
  - `uploads/` (Originale, gezählt für "Dokumente")
  - `annotated/` (vom System erzeugt)
  - `metadata.json` (Basis-Metadaten, Status, Timestamps)
  - `criteria_responses.json` (Ergebnisse/Kriterienstände)
  - `chat_history.json` (Projektchat)
- Startup-Scan:
  - Durchlaufe `data/input/*/` (nur Verzeichnisse).
  - Falls `uploads/` oder `annotated/` fehlt → anlegen.
  - Falls `metadata.json`, `criteria_responses.json`, `chat_history.json` fehlen oder ungültig → mit Defaults neu schreiben.
  - Projektliste wird ausschließlich aus diesem Scan aufgebaut (keine registry-Abhängigkeit).

## Status-Handling
- Status-Felder: `Entwurf`, `Inprüfung`, `Abgeschlossen`.
- Default: `Entwurf` (bei leerem/neuem Projekt).
- Transitions:
  - Öffnen/Bearbeiten im Review → `Inprüfung` (per API-Call setzbar).
  - Nach Abschluss aller Kriterien/Bewertung → `Abgeschlossen` (per API-Call setzbar).

## Dokumentzählung
- "Dokumente"-Spalte zählt nur Dateien in `uploads/` (keine annotated).
- Backend liefert count in Projekt-Liste/Detail.

## APIs (Ergänzungen/Anpassungen)
- Projekte
  - `GET /api/projects` → Liste aus Ordner-Scan, liefert: id, name, applicant, funding_amount, status, documents_count (uploads), last_updated.
  - `POST /api/projects` → neues Projekt anlegen: erzeugt Ordner + Mindestdateien; id generieren (8-stellig, kollisionsfrei).
  - `GET /api/projects/{id}` → Detail inkl. Dokumentliste (uploads), status, metadata.
  - `DELETE /api/projects/{id}` → Ordner löschen (optional, falls benötigt).
  - `POST /api/projects/{id}/status` → Status setzen (`Entwurf`|`Inprüfung`|`Abgeschlossen`).
- Dateien
  - `GET /api/projects/{id}/documents` → aus uploads/ (mit annotated-Hinweis wie bisher), count basiert auf uploads.
  - Upload-Endpoint unverändert, speichert nach uploads/.
- Kriterien-Queue (neu)
  - Enqueue-Varianten:
    - `POST /api/queue/projects/{id}/criteria/{critId}` (ein Kriterium für ein Projekt)
    - `POST /api/queue/projects/{id}/criteria/all` (alle Kriterien für ein Projekt)
    - `POST /api/queue/projects/all/criteria/all` (alle Kriterien für alle Projekte)
  - `GET /api/queue` → Status aller Jobs (pending/running/done/failed), mit project_id, criterion_id, started_at, updated_at, progress, message.
  - Verarbeitung strikt sequentiell pro Queue (FIFO); Backend verwaltet Reihenfolge.
  - Ergebnisse nach Abschluss in `criteria_responses.json` im jeweiligen Projektordner.
  - RAG-Handling pro Job:
    1) VectorStore leeren für andere Projekte (`delete_by_metadata project_id!=current`).
    2) Alle Dateien aus `uploads/` des Zielprojekts ingestieren.
    3) LLM-Prüfung mit Prompt aus Katalog + globaler `kriterien_pruefung`-Richtlinie.
    4) Ergebnis/evidence/annotated in `criteria_responses.json` und ggf. `annotated/` speichern.

- Kriterien-Evaluation
  - Input: `config/criteria_catalog.json` (Felder: id, name, category, kurz, lang, prompt, recommended).
  - Persistenz: `criteria_responses.json` je Projekt; enthält status/score/reason/annotations/evidence.
  - Optional: Summary-Felder auch in metadata.json spiegeln (z.B. last_evaluation, counts).

- Chat
  - Projektchat speichert in `data/input/<id>/chat_history.json` (anstatt global), API unverändert (liest/schreibt diese Datei).

- Globaler Chat (/chat) – Ablauf & Anforderungen
- Speicherort: pro Chat eine JSON-Datei unter `data/chats/`. Laden eines bestehenden Chats lädt vollständiges Verlaufskontext in das LLM.
- Initialisierung neuer Chat-Sessions:
  1) Beim Anlegen/laden eines leeren Chats wird ein Seed geschrieben: system `prompts.global_chat_initial`, assistant `prompts.begruessung`.
  2) Danach normale Frage-Antwort-Runden; jede Nutzerfrage wird mit `prompts.antwort_richtlinie` (meta) an das LLM gegeben.
- Wissensbasis: ausschließlich Global Knowledge (VectorStore bleibt geladen), keine Quellenangabe erforderlich, aber RAG-Kontext wird immer genutzt.
- Edge Cases: Wenn RAG leer/nicht geladen → Anfrage ablehnen mit klarem Fehler; defekte Chat-JSON → neu initialisieren.

- Projektkontext & Chat (/projects/{id}/review)
- RAG-Ladung pro Projekt zwingend, bevor Chat/Kriterien ausgeführt werden:
  1) VectorStore auf Chunks des Zielprojekts beschränken (Löschung anderer project_id).
  2) Uploads ingestieren aus `data/input/<id>/uploads` (docling-Format mit Positionsinformationen, damit Viewer-Anker funktionieren).
- Chat-Verhalten: identisch zum globalen Chat (Seed system + begruessung, `antwort_richtlinie` pro Frage), aber Wissensbasis = Global Knowledge + Projekt-Uploads.
- Quellenpflicht: Antworten aus Projektkontext müssen Quellenanhänge liefern (Dateiname + docling-Position/Page), sonst 400; FE kann dadurch den Dokumentviewer öffnen.
- Bestehende Projekt-Chats werden aus `data/input/<id>/chat_history.json` geladen; kein erneuter Begrüßungsschritt.
- Fehlerfälle: fehlende/ungültige Uploads → klarer Fehler; wenn RAG-Ladung fehlschlägt → Chat/Kriterien ablehnen.

## RAG / LLM Ablauf bei Kriterien-Jobs
- Vor jedem Job sicherstellen:
  - VectorStore nur mit Chunks des Zielprojekts: alte Chunks löschen (project_id-Filter), dann ingest aller uploads/ des Projekts.
- Sequenzielle Beispiele:
  1) K001 @ Projekt123 → ingest uploads/123 → prüfen → speichern in criteria_responses.json.
  2) K002 @ Projekt123 → uploads/123 bereits geladen → prüfen → speichern.
  3) K001 @ Projekt999 → Chunks von 123 löschen → ingest uploads/999 → prüfen → speichern.
- Prompting:
  - Pro Kriterium: `prompt` aus Katalog.
  - Globale Richtlinie: config `prompts.kriterien_pruefung` wird angehängt (Antwortformat/Sprachvorgabe).
  - Optional: system_prompt aus `prompts.global_chat_initial` kann zusätzlich genutzt werden, falls gewünscht.

## Kriterienprüfung – Ablauf & Validierung
- Inputquellen:
  - Rahmenprompt: `prompts.kriterien_pruefung` aus config.
  - Kriteriumsspezifisch: `prompt` aus `config/criteria_catalog.json` für die jeweilige `id`.
- Anfrage-Build pro Job (FIFO in Queue):
  1) Sicherstellen: Projekt-RAG geladen (siehe oben), sonst Fehler.
  2) System/Assistant Message: Rahmenprompt (`kriterien_pruefung`).
  3) User Message: Katalog-Prompt des Kriteriums.
  4) Erwartetes Responseformat ist im Rahmenprompt definiert (Status, Begründung ≤160 Zeichen, Dokument, Referenz als Page/Cell o.ä.).
- Validierung der LLM-Antwort:
  - Antwort muss valides JSON sein und Felder `status` (`rot|gelb|grün`), `begründung`, `dokument`, `referenz` enthalten.
  - Falls invalides JSON oder fehlende Felder: einmalige Wiederholung mit Klartext-Fehlerhinweis "Antwort muss JSON im definierten Schema sein".
  - Wenn zweite Antwort erneut ungültig → Job-Ergebnis mit `status: gelb`, reason: "Keine gültige Antwort vom LLM", evidence leer.
- Statuslogik:
  - `grün` bei eindeutigem Nachweis, `rot` bei klarem Gegenbeleg/fehlender Evidenz, `gelb` bei Unsicherheit oder Formatfehler nach Retry.
  - `score` optional (1.0/0.0/0.5) ableitbar aus Status.
- Persistenz (criteria_responses.json): aktualisiere `criteria_results[<id>]` inkl. timestamps, evaluator, duration, status, reason, evidence und optional `annotated_file*`. Summary-Felder (`evaluated`, `pending`, `status_counts`) konsistent neu berechnen.

## Evidenz & Annotationen
- Jede grün/gelb Antwort mit Referenz erzeugt Evidence-Einträge mit:
  - `dokument` (Dateiname), `dokument_original_path` (uploads-Pfad), `referenz` (z.B. Seite/Zelle/Textstelle), `text_snippet` (kurzer Auszug), `annotated_file`, `annotated_file_path`.
- Annotierte Dateien:
  - Original aus `uploads/` kopieren nach `annotated/` mit Suffix `_annotated.ext`.
  - Fundstelle visuell markieren (docling Positionsdaten nutzen) und Pfade in Evidence zurückschreiben.
  - Bei fehlenden Positionsdaten: Evidence ohne annotated_file, aber Referenz + snippet liefern; Status kann trotzdem grün/gelb sein.
- Fehlerfälle:
  - Wenn Kopie/Annotation fehlschlägt → Job bleibt erfolgreich, aber Evidence vermerkt fehlende Annotation (`annotated_file: null`) und setzt eine Warnung in `message`.
  - Keine Evidence gefunden → Status rot, leeres Evidence-Array.

## Queue-Edge-Cases & Robustheit
- Doppel-Submit desselben Kriteriums während laufendem Job: zweite Anfrage wird ignoriert oder als duplicate pending gekennzeichnet.
- Fehlender Kriterieneintrag in Katalog → Job sofort failed mit klarer Fehlermeldung.
- RAG nicht geladen oder uploads fehlen → Job failed, queue fährt mit nächstem Element fort.
- Persistenzfehler (criteria_responses.json nicht schreibbar) → Job failed, Message enthält Ursache.

## Default-Dateien (beim Anlegen/Heilen)
- metadata.json Beispiel:
  ```json
  {"id":"<id>","name":"<fallback:folder>","applicant":null,"funding_amount":null,"description":null,"status":"Entwurf","created_at":"<iso>","updated_at":"<iso>"}
  ```
- criteria_responses.json Beispiel:
  ```json
  {"project_id":"<id>","summary":{"total":0,"evaluated":0,"pending":0,"status_counts":{}},"criteria_results":{},"last_evaluation":null}
  ```
- chat_history.json: leeres Array `[]` oder Objekt mit `messages: []` (konsistent zum Chat-Router).

## Validierung & Robustheit
- Tolerant gegenüber fehlenden/korrupten JSONs: überschreiben mit Defaults.
- Ignoriere versteckte Dateien; nur echte Unterordner als Projekte.
- Keine Abhängigkeit von registry.json; optionaler Migrations-Helper später.

## Tests (zu implementieren)
- Startup-Scan legt fehlende Strukturen an (uploads/annotated + 3 JSONs) und liefert Projekte.
- Dokumentzählung basiert auf uploads (annotated werden nicht gezählt).
- Status-API setzt/liest Status nur aus metadata.json.
- Queue-API: enqueuen mehrere Kriterien, Polling liefert running/done, Ergebnisse landen in criteria_responses.json.
- Chat persistiert im projektlokalen chat_history.json.

## Nicht in diesem Schritt
- Inhaltliche LLM-Kriterienprüfung (bleibt wie im aktuellen Code), solange Queue nur orchestriert.
- UI-Änderungen: sind im Frontend-Dokument beschrieben.
