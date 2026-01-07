# User Stories & Bug Reports (RAG System Update 2026-01-05)

## Überblick
Dieses Dokument fasst die vom Nutzer gemeldeten Fehler und Anforderungen für das RAG-System (Global & Projektbezogen) zusammen. Es dient als Basis für die folgenden Backend- und Frontend-Arbeiten.

## Bugs & User Stories

### Bug 1: Global RAG - Fehlende Identität (Herbert.txt)
**Beschreibung:**
Nach dem Hochladen einer Datei `herbert.txt` im globalen Wissen (Inhalt: "Ich bin Herbert...") konnte das RAG-System auf die Frage "Wer bist du?" keine Antwort geben ("Ich konnte keine Informationen finden...").
**Erwartetes Verhalten:**
Das System muss die Informationen aus `herbert.txt` finden und antworten: "Ich bin Herbert, der Sachbearbeiter...".
**Implikation:**
- Indexierung prüfen: Wurde die Datei wirklich vektorisiert?
- Retrieval prüfen: Wurde der Chunk gefunden?
- Prompting: Nutzt das LLM den Kontext?

### Bug 2: Global RAG - Identität in neuem Chat
**Beschreibung:**
Auch beim Starten eines *neuen* Chats wurde die Information aus Bug 1 nicht gefunden.
**Erwartetes Verhalten:**
Jeder neue Chat muss Zugriff auf den aktuellen, globalen Wissensbestand haben. Die Vektordatenbank darf nicht "stale" (veraltet) sein.

### Bug 3: Ignorierte System-Prompts & Begrüßung
**Beschreibung:**
Die in den Einstellungen definierten System-Prompts (z.B. "Begrüßung", "Global Chat Initial Prompt", "Antwortrichtlinie") werden ignoriert.
**Erwartetes Verhalten:**
- **Start:** Beim Öffnen des Chats muss der *aktuelle* (in Config definierte) System-Prompt geladen werden.
- **Verlauf:** Bei jeder User-Nachricht muss die "Antwortrichtlinie" (hidden) als Instruktion mitgesendet werden.
- **Begrüßung:** Die konfigurierte Begrüßung muss erscheinen.

### Bug 4: Falsche Quellenbenennung ("Dokument" vs. Dateiname)
**Beschreibung:**
Quellen werden im Chat nur generisch als "Dokument" oder "Quelle X" bezeichnet.
**Erwartetes Verhalten:**
Die Quellenangabe muss den exakten **Dateinamen** (z.B. `herbert.txt`, `richtlinie.pdf`) enthalten.
**Zusatz:** Im Backend ist die genaue Referenz (Seite/Abschnitt) vorhanden, im Frontend reicht der Dateiname (und ggf. Seite bei Mouseover/Expand).

### Bug 5 & 9: Phantom-Quellen (Zu viele / Irrelevante Quellen)
**Beschreibung:**
Es werden pauschal 10 Quellen angezeigt, auch wenn diese irrelevant sind oder gar keinen Bezug zur Antwort haben.
**Erwartetes Verhalten:**
- Nur relevante Quellen (hoher Score) anzeigen.
- Wenn keine relevanten Quellen gefunden werden (Score zu niedrig), keine Quellen anzeigen (oder Hinweis "Keine Quellen").
- Die Anzahl (top_k) sollte ggf. reduziert oder dynamisch gefiltert werden.

### Bug 6: UI Feature - Quellen Toggle (Review View)
**Beschreibung:**
In der Projekt-Ansicht (`/projects/{id}/review`) fehlt die Kontrolle über die Sichtbarkeit der Quellen.
**Erwartetes Verhalten:**
Ein Toggle-Button oder eine klickbare Leiste ("Quellen anzeigen/verbergen"), um die Quellenliste ein- oder auszublenden.

### Bug 7 & 8: Projekt-Kontext Leaking (Kontext-Hygiene)
**Beschreibung:**
Beim Wechsel zwischen Projekt A und Projekt B bleiben Informationen aus Projekt A im RAG-Kontext erhalten ("Leaking").
*Beispiel:* Frage nach Firmenname in Projekt B liefert den Namen aus Projekt A.
**Erwartetes Verhalten:**
- **Projekt-Isolation:** Informationen aus Projekt A dürfen in Projekt B NIEMALS auftauchen.
- **Lifecycle:**
    - Eintritt in Projekt: Lade Projekt-Dokumente (oder nutze strikten Projekt-Filter).
    - Verlassen des Projekts / Wechsel: Entlade Kontext (oder garantiere Filterung).
- **Prozess:** Der User wünscht sich explizit ein Bereinigen ("Rausladen") beim Verlassen. (Technisch sauberer: Strikter Filter `project_id` bei jedem Query).

### Bug 10: Fehlender Lade-Spinner (Review View)
**Beschreibung:**
In der Projekt-Chat-Ansicht fehlt der Lade-Indikator, während die Antwort generiert wird.
**Erwartetes Verhalten:**
Anzeige eines Spinners (analog zum Global Chat), solange auf die Antwort des LLMs gewartet wird.


### Bug 11: Global Chat Quellen-Sichtbarkeit
**Beschreibung:**
Im Global Chat werden Quellen aktuell angezeigt. Der User möchte diese aber *visuell* ausblenden (per CSS `display:none`), damit der Chat "sauberer" wirkt, die Daten aber im Hintergrund (HTML) für Debugging vorhanden bleiben.
**Erwartetes Verhalten:**
- **Global Chat:** Quellen-Container `display: none` (oder via CSS Klasse hidden).
- **Projekt Chat:** Quellen-Container sichtbar (`visible: true`).

### Bug 12: Generische Quellen-Namen ("Dokument")
**Beschreibung:**
Die Quellenanzeige zeigt generische Namen wie "Dokument" statt des echten Dateinamens (z.B. "Herbert.txt").
**Erwartetes Verhalten:**
- Die Quelle muss den echten Dateinamen (`doc_name` aus Metadaten) anzeigen.
- Dubletten vermeiden (wenn eine Datei mehrfach zitiert wird, nur einmal auflisten oder Zählung anzeigen).

### Bug 13: LLM Kontext & Konfiguration
**Beschreibung:**
Das Kontextfenster (1000 Tokens) ist zu klein für komplexe RAG-Anfragen inklusive globaler Prompts.
**Erwartetes Verhalten:**
- `max_tokens` auf **50.000** (oder Maximum des Modells) erhöhen.
- `temperature` auf **0.7** setzen für kreativeres/natürlicheres Antworten.
- Sicherstellen, dass globale Prompts (System Prompt) *immer* im Kontext enthalten sind, auch wenn Chunks geladen werden.

---

## Zusammenfassung der Anforderungen
1.  **RAG-Qualität:** Retrieval muss funktionieren (Bug 1, 2).
2.  **Konfiguration:** Prompts müssen aus `config.yaml` ziehen (Bug 3).
3.  **Quellen:** Korrekte Benennung (Bug 12), Filterung und Visibility (Bug 4, 11).
4.  **Isolation:** Strikte Trennung von Projekt-Kontexten (Bug 7, 8).
5.  **UX:** Quellen-Toggle und Spinner (Bug 6, 10).
6.  **LLM:** Token-Limit erhöhen (Bug 13).
