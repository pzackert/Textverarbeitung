# STARTUP GUIDE (Planned Behavior)

This guide documents the target startup sequence and operational playbook. Implementation is pending.

## 1. Zielbild Startup-Sequenz (deterministisch)
1. **FastAPI hochfahren (Port 8000)** — API erreichbar, aber Requests (außer /api/system/*) werden durch Startup-Guard geblockt, solange status != "ready".
2. **Health LM Studio** — Probe `http://127.0.0.1:1234/v1/models`; Status `lm_studio` = ready/error.
3. **Health Ollama** — Probe `http://localhost:11434/api/tags`; Status `ollama` = ready/error.
4. **ChromaDB Check** — VectorStore init; Status `chromadb` = ready/error.
5. **Modell aus config lesen** — `config/config.yaml` Felder `llm.provider`, `llm.model`, `llm.base_url`, dirs. Status `llm_model` = loading.
6. **Modell laden/verifizieren** — Verfügbare Modelle prüfen (LM Studio: ~/.lmstudio/models; Ollama: ~/.ollama/models) und ggf. fallback Modell wählen; Status update.
7. **OK-Prompt Test** — Ein kurzer Prompt "OK" gegen das geladene Modell; Status `llm_model` = ready/error.
8. **Global Knowledge laden** — POST /api/rag/global/load; Status `rag_pipeline` = loading.
9. **Poll RAG** — GET /api/rag/global/status bis status == "ready"; Status `rag_pipeline` = ready/error.
10. **Systemstatus setzen** — `system_state.global_status = ready`; Startup-Guard hebt Blockade auf.

Fallbacks:
- LM Studio down → versuche Ollama. Beide down → status = error, API bleibt geblockt.
- Modell nicht gefunden → nimm default `openai/gpt-oss-20b` (LM Studio) oder erstes verfügbares Modell, Status mit Warning.
- RAG-Load fail → System bleibt up, aber `rag_pipeline` = error; status = error.
- ChromaDB fail → kritischer Fehler, status = error.

## 2. Konfiguration
- Datei: [config/config.yaml](config/config.yaml)
- Wichtige Schlüssel:
  - `llm.provider`: `lm_studio` | `ollama`
  - `llm.base_url`: z.B. `http://127.0.0.1:1234` (LM Studio) oder `http://localhost:11434` (Ollama)
  - `llm.model`: primäres Modell
  - `llm.models_dir`: Pfad zu Modellen (`~/.lmstudio/models` oder `~/.ollama/models`)
- Default Zielmodell: `openai/gpt-oss-20b` (LM Studio). Falls fehlt, per UI/CLI Modell hinzufügen oder Fallback nutzen.

## 3. Frontend-Integration
- Poll **GET /api/system/status** alle 2s, solange `status` ≠ `ready`.
- UI zeigt Phasen/Progress je Komponente (lm_studio, ollama, chromadb, llm_model, rag_pipeline) und Fehlertexte.
- Erst wenn `status == "ready"`, weitere API-Flows freigeben.

## 4. Fehlerbehandlung (Beispiele)
- **LM Studio offline:** Status `lm_studio=error`; Sequenz versucht Ollama. Wenn auch error → global status error, Hinweis "LLM backend unreachable".
- **Modell fehlt:** Status `llm_model=error`; versuche Fallback-Modell; log Warning; wenn kein Modell, global status error.
- **ChromaDB down:** status error, Startup stoppt; Hinweis "Vector store unavailable".
- **RAG load fail:** `rag_pipeline=error`; global status error; API bleibt geblockt oder liefert 503 mit Fehlgrund.

## 5. Debugging-Tipps
- Prüfe laufende Dienste: `lsof -i :1234`, `lsof -i :11434` oder `ps aux | grep ollama` / LM Studio UI.
- Teste LLM direkt: `curl http://127.0.0.1:1234/v1/models` oder `curl http://localhost:11434/api/tags`.
- ChromaDB: sicherstellen, dass `data/chromadb` beschreibbar ist und keine Port-Kollision besteht.
- Logs: `logs/ifb_profi.log` (laut config), plus FastAPI stdout.
- Bei Startup-Error: erneut `POST /api/system/startup` triggern, dann Status pollen.

## 6. Offene Implementierungsaufgaben
- Startup-Service orchestrieren (Sequenz, Fallbacks, OK-Prompt, Global-Load, Polling).
- Middleware-Guard einbauen, die Nicht-System-Routen blockt bis ready.
- Status-Response erweitern (phase, errors, timestamps).
- Konfig-Pfade harmonisieren (LM Studio vs Ollama Model dirs) und Fallback-Modell Logik.
- Tests: automatisierter Startup-Flow (tmp/test_startup.py) mit Mocks/Stubs für LM Studio/Ollama/Chroma/RAG.
