# Backend Übergabeprotokoll

## Implementierte Funktionen
- Provider-Scan (LM Studio + Ollama) inkl. API-Check und Fallback-Logik im Startup.
- Model-Listing kombiniert Live-APIs und lokale Dateien (`/api/settings`, `/api/settings/models`).
- Settings-API: LLM (Provider/Modell/Hyperparameter), RAG (chunk_size, chunk_overlap, top_k), Prompts (inkl. Begrüßung, global_chat_initial, antwort_richtlinie).
- Startup-Trigger `/api/system/startup` und Status `/api/system/status` mit Komponenten lm_studio, ollama, chromadb, llm_model, rag.
- Global-Chat: Seedet neue Chats mit Prompts aus Config, nutzt Antwort-Richtlinie/System-Prompt beim Query.
- Chat-Dateien in `data/chats` (create/load/delete), bereits über Chat-Router nutzbar.

## Wichtige Endpunkte
- GET /api/settings — komplette Config + available_models
- GET /api/settings/models — reine Modellliste
- POST /api/settings/llm — {provider?, model, temperature, max_tokens, timeout} -> restart_required
- POST /api/settings/rag — {chunk_size, chunk_overlap, top_k} -> restart_required
- POST /api/settings/prompts — Prompts anpassen -> restart_required
- POST /api/system/startup — Neustart/Startup-Sequenz (asynchron)
- GET /api/system/status — Fortschritt/Fehler je Komponente
- Chats: /api/chats/global (list, create, get, message, delete), /api/chats/project/... 

### Frontend-Hinweise (Restart & Status)
- Nach jedem Settings-POST erscheint restart_required=true. FE zeigt Hinweis + Button "System neu starten".
- Button ruft POST /api/system/startup. Anschliessend Polling GET /api/system/status (1-2s Intervall), bis status=ready oder error.
- status enthält Komponenten: lm_studio, ollama, chromadb, llm_model, rag. Anzeigen: status, message, progress, duration_sec.
- Fehlermeldungen sichtbar machen, kein stilles Verschwinden (insb. wenn kein Provider erreichbar).

**Beispiel-Calls (für FE-Dev/Mock):**
- Restart trigger:
	- Request: `POST /api/system/startup`
	- Response: `{ "message": "Startup initiated", "status": "initializing" }`
- Status poll:
	- Request: `GET /api/system/status`
	- Response (Auszug):
		```json
		{
			"status": "initializing",
			"step": 3,
			"total_steps": 6,
			"current": "Prüfe Ollama Verfügbarkeit...",
			"components": [
				{"name": "lm_studio", "status": "ready", "message": "Verbunden (API verfügbar)", "progress": 100},
				{"name": "ollama", "status": "loading", "message": "Wird gestartet...", "progress": 30},
				{"name": "chromadb", "status": "pending"},
				{"name": "llm_model", "status": "pending"},
				{"name": "rag", "status": "pending"}
			]
		}
		```

## Testabdeckung
- test_api/test_settings.py — Settings lesen/schreiben + Modellliste
- test_api/test_startup_providers.py — 4 Provider-Szenarien (LM+Ollama, nur LM, nur Ollama, keiner) mit Startup-Status
- test_api/test_chat_and_settings_flows.py — Chat-Create/List/Delete, RAG/Non-RAG Messages (Fake LLM), Prompt-Seed, Hyperparameter-/RAG-Profile, Modelle-Liste (API+Files), Mehr-Chat-Sequenzen

## Hinweise für das Frontend
- Nach jedem Settings-POST Hinweis „Restart erforderlich“ anzeigen, dann `/api/system/startup` aufrufen und `/api/system/status` pollen.
- Modelle für Dropdown aus GET /api/settings/models, gruppiert nach provider; aktuelles Modell aus GET /api/settings.
- Neue Chats liefern initiale System-/Begrüßungsnachricht aus Config-Prompts; antwort_richtlinie wird beim Generieren mitgegeben.
- Chats können gelöscht werden (DELETE /api/chats/global/{id}); FE soll Liste aktualisieren.
- Edge Cases: kein Provider erreichbar -> status=error; fehlendes Modell -> llm_model Komponente meldet Fehler; fehlende Datenordner -> chromadb Fehler; FE soll Hinweise anzeigen.
- Tests nutzen Fake LLM für schnelle Durchläufe; reale Provider-Checks bleiben in test_startup_providers.py.

## Offene Punkte / Annahmen
- Hello-World-Tests pro Modell sind über Startup+Provider erreichbar; weitere Modell-spezifische Limits (max_tokens) müssen ggf. manuell hinterlegt werden.
- Richtlinien werden als Teil des Prompting übergeben, nicht im sichtbaren Chat-Text angezeigt.
