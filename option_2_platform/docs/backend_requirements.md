# Backend Anforderungen & Testplan

## Rahmen
- Config-Datei: config/config.yaml (Provider, Modelle, Hyperparameter, RAG, Prompts)
- Relevante Endpunkte: GET /api/settings, GET /api/settings/models, POST /api/settings/llm, POST /api/settings/rag, POST /api/settings/prompts, POST /api/system/startup, GET /api/system/status
- Modellquellen: Live-APIs (LM Studio /v1/models, Ollama /api/tags) + lokale Dateien (lm_studio.models_dir, ollama.models_dir)
- Datenordner: data/global_knowledge (RAG), data/chats (globale Chat-Sessions), data/input/<project_id>/chat_history.json (Projektchat)

## 1) Provider-Verfuegbarkeit & Startup-Robustheit
- Anforderung: Beim Startup beide Provider pruefen; mindestens einer muss bereit sein. Klare Fehler, falls keiner erreichbar oder Pfad/Endpoint falsch.
- Expected Result: Systemstatus READY wenn mind. ein Provider erreichbar; ERROR wenn keiner. Klarer Hinweis im Status.
- Use Cases:
  1. LM Studio und Ollama verfuegbar -> beide READY, aktiver Provider aus config.llm.provider.
  2. Nur LM Studio verfuegbar -> LM READY, Ollama SKIPPED/ERROR, aktiver Provider lm_studio.
  3. Nur Ollama verfuegbar -> Ollama READY, LM SKIPPED/ERROR, aktiver Provider ollama.
  4. Keiner verfuegbar -> Startup bricht mit status=error und Meldung.
- Tests: Trigger POST /api/system/startup, dann GET /api/system/status fuer jeden Case (Mock Ports oder real Services). Erwartete Komponente: lm_studio, ollama, chromadb, llm_model, rag.

## 2) Modelle laden und Hello-World je Modell
- Anforderung: Jedes verfügbare Modell (aus /api/settings/models) einmal laden und einfache Prompt-Ausgabe pruefen ("Hello World").
- Expected Result: Alle Modelle liefern Antwort; fehlschlagende Modelle werden im Status/Log markiert.
- Use Cases (mind. 8-9 Modelle, je Provider separat):
  - Fuer jedes Modell: POST /api/settings/llm (provider, model, temp=0.1, max_tokens=64, timeout=60), dann POST /api/system/startup. Danach kurzer Aufruf gegen aktiven Provider (LM: /v1/chat/completions, Ollama: /api/generate) oder vorhandene Chat-API, Prompt "Hello World".
  - Falls Modell nicht im Provider vorhanden -> erwartete Fehlermeldung und kein READY.

## 3) Hyperparameter-Steuerung (LLM)
- Anforderung: Temperatur, max_tokens, timeout pro Modell setzbar via config/API, Neustart zwingend.
- Expected Result: Neue Werte greifen nach Restart; werden in GET /api/settings sichtbar; Aufruf liefert Antwort ohne Timeout.
- Use Cases (Beispiele):
  1. ministral-3b-lmshare, temp 0.7, max_tokens 10000, timeout 120 -> speichern, restart, Hello World.
  2. openai/gpt-oss-20b, temp 0.5, max_tokens 20000, timeout 120 -> speichern, restart, Hello World.
  3. qwen3-vl-4b, temp 0.2, max_tokens 4096, timeout 90 -> speichern, restart, Hello World.
- Validierung: Nach POST /api/settings/llm -> restart -> GET /api/settings pruefen; Antwortzeiten im Test messen.

## 4) RAG-Parameter (chunk_size, chunk_overlap, top_k)
- Anforderung: Werte via /api/settings/rag setzen, Persistenz in config, Neustart anstossen.
- Expected Result: Werte werden uebernommen und beeinflussen Ergebnisse (z.B. Chunk-Anzahl). Systemstatus bleibt READY nach Restart.
- Use Cases:
  1. Medium: chunk_size 1000, overlap 50, top_k 10
  2. Klein/fein: chunk_size 400, overlap 100, top_k 15
  3. Gross/grob: chunk_size 2000, overlap 0, top_k 5
- Tests: POST /api/settings/rag, dann /api/system/startup, danach RAG-Abfrage (z.B. globaler Chat oder direkter Retrieval-Test) gegen data/global_knowledge.

## 5) Prompts & Antwort-Richtlinien
- Anforderung: Prompts aus config.prompts muessen in Chat-Initialisierung einfliessen; antwort_richtlinie soll bei jeder Antwort als system/meta-Instruction gezogen werden (nicht im sichtbaren Chat-Text).
- Expected Result: Begruessung wird beim Start eines neuen Chats gesendet; Antworten halten die Richtlinie (kurz, deutsch, Quellen, gestehen bei Nichtwissen). Anpassungen via /api/settings/prompts und Neustart wirksam. Global-Chat nutzt RAG standardmäßig; wenn Global Knowledge nicht geladen → klarer Fehler.
- Use Cases:
  1. Begruessung aendern -> neuer Chat startet mit neuer Begruessung.
  2. global_chat_initial aendern -> erster Systemturn reflektiert neue Rolle.
  3. antwort_richtlinie aktiv -> beliebige Frage (3 + 3 * 4) liefert kurze Antwort nach Schema.

## 6) Chat-Sessions (data/chats + data/input/<id>)
- Anforderung: Globale Chats als JSON-Dateien in data/chats, Projektchats projektlokal in data/input/<id>/chat_history.json. Create/Load/Delete via API. Kein zusaetzliches Directory-Index, einfache Dateiliste reicht.
- Expected Result: Neue Chats legen Datei am richtigen Ort an; Laden liest Kontext + Begruessung; Loeschen entfernt Datei.
- Use Cases:
  1. Neuen globalen Chat anlegen -> Datei entsteht in data/chats, Begruessung enthalten.
  2. Neuen Projektchat laden/erstellen -> Datei entsteht unter data/input/<id>/chat_history.json, Begruessung + system_prompt werden gesetzt, Quellenpflicht fuer Antworten; wenn Projekt-RAG keine Treffer liefert → Fehlermeldung (503) statt leerer Antwort.
  3. Bestehenden Chat laden -> Kontext wird wiederhergestellt, kein erneutes Prompting noetig.
  4. Chat loeschen -> Datei entfernt, Liste aktualisiert.

## 7) Fehler- und Restart-Flows
- Anforderung: Alle schreibenden Settings-Calls liefern restart_required=true. Frontend soll POST /api/system/startup nutzen. Bei Provider-Fehlern klare Messages im Status.
- Expected Result: Konsistente Statusmeldungen; keine stillen Fehler.

## 8) Uebergabeprotokoll (Backend -> Frontend)
- Inhalt: implementierte Anforderungen, Liste der Endpunkte, Beispiel-Requests, bekannte Limits (Token je Modell), offene Punkte.
- Artefakt: Markdown im Repo (z.B. docs/backend_handover.md) nach Abschluss aktualisieren.

## ToDos fuer Backend (konkret)
- [ ] Tests fuer Provider-Cases (4 Szenarien) mit /api/system/startup + /status.
- [ ] Modell-Load/Hello-World Tests fuer alle verfügbaren Modelle.
- [ ] Hyperparameter-Tests (3 Use Cases) mit Restart.
- [ ] RAG-Parameter-Tests (3 Use Cases) mit Restart und simplem Retrieval.
- [ ] Prompt/Richtlinien-Test (Begruessung, global_chat_initial, antwort_richtlinie).
- [ ] Chat-Datei-Flow Tests (create/load/delete) auf data/chats.
- [ ] Uebergabeprotokoll an Frontend erstellen (inkl. Beispiel-Curls).
