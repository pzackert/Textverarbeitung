# Master Test Plan: 20+ End-to-End Szenarien
**Status:** DRAFT (Warte auf Freigabe)
**Umfang:** 20+ Detaillierte Testfälle (TC)
**Prinzip:** Jeder Testfall beschreibt den Vollen Systemzyklus (Boot -> Load -> Interaction).

---

## I. Global Knowledge & System Startup (TC-01 bis TC-05)

### TC-01: Globaler Kaltstart & Identität ("Der Herbert-Test")
**Ziel:** Verifizieren, dass globales Wissen nach einem kompletten Reset automatisch geladen wird.
**Bug Ref:** Bug 1, 12
1. **Systemzustand:** Server gestoppt. Datenbank (`data/chromadb`) gelöscht. `data/global_knowledge/herbert.txt` existiert.
2. **System Start:** 
   - Start `uvicorn`.
   - `SystemStateManager` erkennt leere DB.
   - **Auto-Load** startet (Logs: "Auto-loading...").
   - Warten bis Status `/api/rag/global/status` = `ready`.
3. **Frontend:** Öffne Dashboard (`/`). Prüfe Status-Badge "RAG Bereit".
4. **Interaktion:** Öffne Global Chat (`/chat`).
5. **Eingabe:** "Wer ist Herbert?"
6. **Erwartung:** Antwort "Herbert ist der Sachbearbeiter..." + Quelle `herbert.txt`.

### TC-02: RAG-Verfügbarkeit nach Neustart (Persistenz)
**Ziel:** Prüfen, dass bereits indizierte Daten bei Neustart *nicht* neu geladen werden müssen (Zeitersparnis).
**Bug Ref:** Bug 2
1. **Systemzustand:** Server läuft (TC-01 erfolgreich). Daten sind indiziert.
2. **System Aktionen:**
   - Stoppe Server (SIGTERM).
   - Starte Server neu.
3. **Startup:** `SystemStateManager` prüft DB. Ergebnis: `chunks > 0`.
4. **Logik:** Überspringe Auto-Load (Logs: "Found X chunks, skipping load").
5. **Frontend:** Öffne Chat sofort.
6. **Erwartung:** Anfrage "Wer ist Herbert?" funktioniert **sofort** (< 2s nach Boot).

### TC-03: Upload neuer Globaler Dokumente
**Ziel:** Hinzufügen von Wissen im laufenden Betrieb.
1. **Systemzustand:** Server läuft. Global Chat offen.
2. **Frontend:** Einstellungen (`/settings`).
3. **Aktion:** Upload `neue_richtlinie.pdf`.
4. **Prozess:**
   - `IngestPipeline` verarbeitet Datei.
   - Status wechselt kurz auf `loading`.
   - Vektoren werden hinzugefügt.
5. **Interaktion:** Global Chat -> "Was steht in der neuen Richtlinie?".
6. **Erwartung:** Korrekte Antwort aus dem neuen PDF.

### TC-04: Chat bei fehlendem Wissen ("Wwr bist du?")
**Ziel:** Prüfen der Fehlerkultur bei leeren Suchergebnissen.
**Bug Ref:** User Complaint (503), Bug 13
1. **Systemzustand:** Server läuft. Alles geladen.
2. **Interaktion:** Global Chat (`/chat`).
3. **Eingabe:** "Wer bist du?" (Tippfehler/Unsinn).
4. **RAG:** Findet keine Dokumente (Score < Threshold).
5. **Erwartung:**
   - **KEIN** 500/503 Fehler.
   - Antwort: "Entschuldigung, ich habe keine Informationen gefunden."
   - Quellen-Liste ist leer.

### TC-05: Löschen von Globalem Wissen
**Ziel:** Sicherstellen, dass gelöschtes Wissen nicht mehr gefunden wird (Amnesie).
1. **Systemzustand:** Server läuft. `herbert.txt` ist bekannt.
2. **Frontend:** Einstellungen (`/settings`).
3. **Aktion:** Lösche `herbert.txt` aus der Liste.
4. **Backend:** `DELETE /api/rag/global/file` -> Löscht Vektoren aus ChromaDB.
5. **Interaktion:** Global Chat -> "Wer ist Herbert?".
6. **Erwartung:** Antwort: "Ich weiß es nicht." (Wissen erfolgreich entfernt).

---

## II. Projekt-RAG & Isolation (TC-06 bis TC-10)

### TC-06: Neues Projekt anlegen & Initialisieren
**Ziel:** Projekt-Container erstellen und RAG vorbereiten.
1. **Systemzustand:** Server läuft. Dashboard offen.
2. **Aktion:** "Neues Projekt". Name "Hausbau Müller".
3. **Dateisystem:** Backend erstellt Ordner `data/input/{id}`.
4. **Upload:** User lädt `antrag_mueller.pdf` hoch.
5. **Ingest:** System startet Projekt-Ingest automatisch (oder via Klick).
6. **Erwartung:** Projekt-Status wechselt auf "RAG Bereit".

### TC-07: Projekt A Isolation (Leakage Test)
**Ziel:** Projekt A (Müller) darf nichts von Projekt B (Schulze) wissen.
**Bug Ref:** Bug 7, 8
1. **Systemzustand:** Projekt A (`antrag_mueller.pdf`) und Projekt B (`geheim_schulze.txt`) sind indiziert.
2. **Interaktion:** Öffne Projekt A Review (`/projects/A/review`).
3. **Eingabe:** "Was steht im Geheimnis von Schulze?".
4. **Backend:** Filter `project_id == A`.
5. **Erwartung:** "Keine Informationen gefunden." (Schulze-Daten sind unsichtbar).

### TC-08: Projekt B Zugriff (Verifikation)
**Ziel:** Projekt B findet SEINE Daten.
**Bug Ref:** Bug 7, 8
1. **Systemzustand:** Siehe TC-07.
2. **Interaktion:** Öffne Projekt B Review (`/projects/B/review`).
3. **Eingabe:** "Was steht im Geheimnis von Schulze?".
4. **Erwartung:** Korrekte Antwort mit Quelle `geheim_schulze.txt`.

### TC-09: Hybride Suche (Projekt + Global)
**Ziel:** Kombinierte Antwort prüfen.
**Bug Ref:** Bug 5
1. **Systemzustand:** Server läuft. Global: `richtlinie.pdf`. Projekt: `antrag.pdf`.
2. **Interaktion:** Projekt Chat (`/projects/A/review`).
3. **Eingabe:** "Entspricht der Antrag der Richtlinie?".
4. **Backend:** Retrieval sucht in A UND Global.
5. **Erwartung:** Antwort zitiert `antrag.pdf` UND `richtlinie.pdf` in den Quellen.

### TC-10: Ingest-Fehler Handling (Korrupte Datei)
**Ziel:** Systemstabilität bei kaputten PDFs.
1. **Aktion:** Upload `kaputt.pdf` (0 Byte oder Binärmüll).
2. **Ingest:** Pipeline startet.
3. **Fehler:** Parser wirft Exception.
4. **Erwartung:**
   - Status: "Fehler" (Rot) im Dashboard/Projekt.
   - System stürzt **nicht** ab.
   - Anderes Projekt ist weiterhin nutzbar.

---

## III. Chat Features & Dokumente (TC-11 bis TC-15)

### TC-11: Exakte Quellenbenennung
**Ziel:** Dateinamen statt generischer Platzhalter.
**Bug Ref:** Bug 4, 12
1. **Systemzustand:** TC-01 (Herbert) durchgeführt.
2. **Interaktion:** Chat -> "Wer ist Herbert?".
3. **Erwartung:** In der Quellenliste steht exakt `herbert.txt`, nicht "Dok 1".

### TC-12: Chat Lösch-Performance (Optimistic UI)
**Ziel:** Sofortiges Feedback beim Löschen.
**Bug Ref:** Bug 1
1. **Systemzustand:** 5 alte Chats in der History.
2. **Aktion:** Klick auf "Löschen" beim obersten Chat.
3. **Bestätigen:** "Ja".
4. **Erwartung:** Chat verschwindet **sofort** (< 50ms) aus der Liste. Kein Lag.

### TC-13: Spinner & Lade-Indikator
**Ziel:** Feedback bei längerer Generierung.
**Bug Ref:** Bug 10
1. **Systemzustand:** Server läuft.
2. **Eingabe:** "Schreibe eine sehr lange Zusammenfassung..." (Lange Generierung).
3. **UI:** 
   - Während LLM rechnet: "Spinner" / "Wird geschrieben..." ist sichtbar.
   - Chat-Input ist disabled oder zeigt "Busy".
4. **Erwartung:** Nutzer weiß, dass System arbeitet.

### TC-14: Source Toggle (Sichtbarkeit)
**Ziel:** Quellen ein/ausblenden.
**Bug Ref:** Bug 6, 11
1. **Interaktion:** Projekt Review Chat.
2. **Setup:** Eine Antwort mit Quellen liegt vor.
3. **Aktion:** Klick auf "Quellen verbergen" (falls Feature aktiv) oder Prüfung des Layouts.
4. **Erwartung:** Quellen sind sichtbar (da für Review essentiell).

### TC-15: PDF Viewer Deep-Link
**Ziel:** Klick auf Quelle öffnet Dokument.
1. **Systemzustand:** Chat-Antwort mit Quelle `antrag.pdf` (Seite 3).
2. **Aktion:** Klick auf den Quellen-Chip im Chat.
3. **Viewer:** Linke Fensterhälfte lädt `antrag.pdf`.
4. **Erwartung:** Dokument wird angezeigt (idealerweise auf Seite 3 gescrollt).

---

## IV. Konfiguration & Settings (TC-16 bis TC-20)

### TC-16: Prompt Customization (System Prompt)
**Ziel:** Admin ändert Verhalten.
**Bug Ref:** Bug 3
1. **Aktion:** Bearbeite `config.yaml`. Setze `prompts.begruessung` = "Servus!".
2. **Restart:** Server neustarten.
3. **Interaktion:** Neuer Chat starten.
4. **Erwartung:** Erste Nachricht des Bots ist "Servus!".

### TC-17: Token Limit Konfiguration (Complex RAG)
**Ziel:** LLM Context Limit erhöhen.
**Bug Ref:** Bug 13
1. **Aktion:** Config `llm.max_tokens` = 4096.
2. **Restart:** Server neustarten.
3. **Interaktion:** Stelle Frage zu sehr langem Dokument (30 Seiten).
4. **Erwartung:** Antwort bricht nicht ab, Fehler "Context Limit" tritt nicht auf.

### TC-18: Settings Read-Only Check
**Ziel:** Verhindern, dass User im UI Config kaputt machen.
1. **Interaktion:** Navigiere zu `/settings`.
2. **UI Check:** 
   - Prompt-Felder sind ausgegraut/read-only.
   - "Speichern" Buttons entfernt (außer für Knowledge Upload).
3. **Erwartung:** Konfiguration ist sicher vor User-Eingriffen.

### TC-19: Warteschlange (Queue) Verhalten
**Ziel:** Parallele Requests.
1. **Aktion:** Starte "Prüfung Kriterium 1" für Projekt A.
2. **Sofort danach:** Starte "Prüfung Kriterium 1" für Projekt B.
3. **Erwartung:** Beide Jobs landen in Queue, werden nacheinander (oder parallel, je nach Worker) abgearbeitet. Kein Crash.

### TC-20: Queue Duplikate
**Ziel:** Verhindern doppelter Arbeit.
1. **Aktion:** Starte "Prüfung Kriterium 1" für Projekt A.
2. **Sofort danach:** Klicke nochmals auf den Button.
3. **Erwartung:** Toast-Meldung "Prüfung läuft bereits". Job wird nicht doppelt gestartet.
