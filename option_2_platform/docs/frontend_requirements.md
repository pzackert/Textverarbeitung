# Frontend Anforderungen & Testplan

## Rahmen
- Backend-Endpunkte: GET /api/settings, GET /api/settings/models, POST /api/settings/llm, POST /api/settings/rag, POST /api/settings/prompts, POST /api/system/startup, GET /api/system/status
- Datenquellen: Modelle (Provider + Name + Source), Prompts, RAG-Settings, Chats (data/chats JSON)
- Ziel: Alle Funktionen per UI bedienbar; nach Speichern Neustart anstossen.

## 1) Provider & Modell-Auswahl
- Anforderungen: Dropdown nach Provider gruppiert; Modelle aus GET /api/settings/models (liefert Live-API + lokale Dateien). Provider-Switch und Model-Switch via POST /api/settings/llm.
- Expected Result: Alle verfügbaren Modelle werden angezeigt; aktuelles Modell aus GET /api/settings als Default.
- Use Cases:
  1. Beide Provider aktiv -> UI zeigt zwei Gruppen, Auswahl beliebig; Speichern -> Hinweis "Restart erforderlich" -> Button/Action ruft POST /api/system/startup.
  2. Nur ein Provider aktiv -> UI blendet anderen aus oder markiert ihn als offline.
  3. Kein Provider -> UI zeigt Fehlerhinweis (aus /api/system/status), Speichern gesperrt.

## 2) Modelle testen (Hello World)
- Anforderungen: UI-Action "Test Hello World" mit aktuellem Provider/Modell; nutzt bestehenden Chat-API-Call oder direkten Provider-Call.
- Expected Result: Antwort sichtbar; Fehler werden angezeigt.
- Use Cases: Test je Modell aus Liste (mind. 8-9 Modelle). Ergebnisflag je Modell anzeigen (ok/failed).

## 3) Hyperparameter (Temperatur, max_tokens, Timeout)
- Anforderungen: Editierbar im UI, gespeicherte Werte via GET /api/settings; Speichern mit POST /api/settings/llm; danach Restart anbieten.
- Expected Result: Werte werden angezeigt und nach Reload beibehalten.
- Use Cases: Drei Presets (z.B. 0.7/10000/120, 0.5/20000/120, 0.2/4096/90) wählbar und testbar per Hello-World.

## 4) RAG-Parameter
- Anforderungen: chunk_size, chunk_overlap, top_k konfigurierbar; POST /api/settings/rag; Restart-Button danach.
- Expected Result: Werte sichtbar und persistent.
- Use Cases: Drei Profile (medium, fein, grob) wie im Backend-Dokument; nach Speichern Neustart triggern.

## 5) Prompts & Antwort-Richtlinien
- Anforderungen: Prompts-Formular (begruessung, global_chat_initial, antrags_chat_initial, antwort_richtlinie, kriterien_pruefung); POST /api/settings/prompts; Restart-Hinweis. Richtlinie soll pro Antwort angewendet werden (Backend liefert Feature/gibt Status an).
- Expected Result: Neue Begruessung erscheint beim Start eines neuen Chats; Antworten folgen Richtlinie.
- Use Cases: Begruessung aendern und neuen Chat starten; global_chat_initial aendern und ersten Turn pruefen; antwort_richtlinie pruefen mit kurzer Frage.

## 6) Chat-Sessions
- Anforderungen: Globale Chats liegen in data/chats, Projektchats projektlokal in data/input/<id>/chat_history.json. Aktionen: Neu, Laden, Loeschen. Beim Laden eines leeren Chats wird ein Seed angelegt (system `prompts.global_chat_initial`, assistant `prompts.begruessung`).
- Expected Result: Dateien werden angezeigt, Laden rekonstruiert Chat inkl. Seed; Projektchat-Antworten müssen Quellen liefern, sonst 400. Loeschen entfernt Datei.
- Use Cases: Globalen Chat anlegen/speichern/laden/loeschen; Projektchat laden/erste Frage stellen (Quellenpflicht prüfen).

## 7) Restart-Flow & Status-Anzeige
- Anforderungen: Nach jedem Settings-POST Hinweis "Restart erforderlich"; Button ruft POST /api/system/startup; Status-Poll via GET /api/system/status (Komponenten lm_studio, ollama, chromadb, llm_model, rag) mit Fortschritt/Fehleranzeige.
- Expected Result: UI zeigt klar READY/ERROR, progress je Komponente, Fehlermeldungen sichtbar.

## 8) Uebergabe & Pruefung
- Backend liefert Uebergabeprotokoll (siehe docs/backend_requirements.md bzw. backend_handover). Frontend prueft:
  - Alle Endpunkte erreichbar.
  - Settings-Formulare schreiben und nach Reload konsistent.
  - Restart-Button triggert Startup und Status wechselt zu READY.
  - Modell-Liste deckt sichtbare Provider-Modelle ab.
  - Chats koennen erstellt/geladen/geloescht werden.

## Beispiel-API-Aufrufe (fuer Tests/Dev)
- Modelle laden: GET /api/settings/models
- Aktuelle Settings: GET /api/settings
- Provider/Modell speichern: POST /api/settings/llm {"provider":"lm_studio","model":"mistral-3-3b","temperature":0.3,"max_tokens":1024,"timeout":60}
- RAG speichern: POST /api/settings/rag {"chunk_size":1000,"chunk_overlap":50,"top_k":10}
- Prompts speichern: POST /api/settings/prompts {...}
- Neustart: POST /api/system/startup
- Status: GET /api/system/status
