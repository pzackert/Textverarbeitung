# Frontend Task Instructions (RAG UI Improvements)

## Kontext
Nachdem das Backend die Daten korrekt liefert (gefilterte Quellen, korrekte Prompt-Antworten), muss das Frontend die UX verbessern.
Fokus liegt auf Transparenz (Quellen benennen), Kontrolle (Quellen ein/ausblenden) und Feedback (Spinner).

## Zu bearbeitende Dateien (Primär)
- `frontend/templates/project_review.html` (Projekt-Chat Logic & UI)
- `frontend/static/js/main.js` (Falls ausgelagert, sonst Inline-JS in Templates)

## Aufgabenpakete

### 1. Feature: Lade-Spinner im Projekt-Chat (Bug 10)
**Ziel:** Konsistenzi mit Global Chat. User soll sehen, dass generiert wird.
- **Ist-Zustand:** Nachricht wird gesendet, UI bleibt statisch bis Antwort da ist.
- **Soll-Zustand:**
    1. User sendet Nachricht.
    2. Ein Platzhalter (Spinner / "Schreibe..."-Animation) wird am Ende des Chat-Verlaufs angehängt.
    3. Bei Erhalt der Antwort wird der Spinner durch die Antwort ersetzt.
- **Umsetzung:**
    - Alpine.js `isLoading` Variable nutzen.
    - Template Block: `<div x-show="isLoading" class="...">...Spinner SVG...</div>`.
    - Sicherstellen, dass `isLoading = false` auch im Fehlerfall gesetzt wird!

### 2. Feature: Quellen-Toggle & Anzeige (Bug 6, 4, 5, 9)
**Ziel:** Quellen ausblenden können ("Cleaner Chat") und korrekte Namen anzeigen.
- **Soll-Zustand:**
    - UI-Element (Button/Icon) "Quellen anzeigen" (Default: On oder Off, User-Präferenz merken wäre nice, aber Session reicht).
    - Wenn aktiv: Liste der Quellen unter der Antwort rendern.
    - **WICHTIG (Bug 4 Fix):** Die Quellenanzeige muss den `source.document` Wert (Dateiname) anzeigen, nicht "Dokument 1".
    - **WICHTIG (Bug 5 Fix):** Nur Quellen anzeigen, die vom Backend geliefert werden. Wenn Backend leere Liste liefert, nichts anzeigen. (Keine 10 leeren Platzhalter rendern!).

### 3. Feature: Projekt-Kontext Bereinigung (Bug 7, 8 Support)
**Ziel:** Visuelles Feedback, dass Kontext gewechselt wurde.
- **Soll-Zustand:**
    - Wenn der User `/projects/{id}/review` verlässt (z.B. Click auf "Zurück" oder Nav-Link), sollte idealerweise ein expliziter "Context Cleared" Hook gefeuert werden, falls wir das via API lösen.
    - Falls Backend das stateless (via Filter) löst, ist hier nichts zu tun, außer sicherzustellen, dass beim Laden der Seite der Chat-Verlauf *dieses* Projekts geladen wird (und nicht der alte Cache).
    - Prüfe: Wird `chat_history` aus `project_service` sauber initialisiert?

## Vorgehen
1.  **Spinner implementieren:** Quick Win.
2.  **Quellen-Logik überarbeiten:**
    - Prüfe JSON-Response vom Backend (`sources` Array).
    - Iteriere nur über dieses Array.
    - Zeige `source.document` als Titel.
    - Implementiere Toggle-Button (`x-data="{ showSources: true }"`).

**Output:** Responsives Frontend mit Lade-Indikator und sauberer Quellen-Darstellung.
