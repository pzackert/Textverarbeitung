# Anforderungen: Startup-Sequenz & Dashboard

**Projekt:** IFB PROFI - KI-gestützte Fördermittelprüfung  
**Bereich:** Backend & Frontend Integration  
**Zielgruppe:** Backend-Entwickler

---

## Übersicht

Das System hat eine definierte Startup-Sequenz, die technische Komponenten nacheinander lädt. Diese Sequenz wird bei Erstaufruf oder manuellem Neustart durchgeführt. Das Dashboard ist erst nach erfolgreichem Start verfügbar.

---

## Anforderung 1: Startup-Sequenz mit UI-Feedback

Die Startup-Sequenz lädt alle technischen Komponenten sequenziell. Jede Komponente meldet Status und relevante Informationen an die UI.

### Komponenten in Ladereihenfolge:

| Nr | Komponente | UI-Anzeige bei Erfolg | UI-Anzeige bei Fehler |
|----|------------|----------------------|----------------------|
| 1 | Model Scanner | "X Modelle gefunden" | "Kein Modell vorhanden" oder "Modell kann nicht geladen werden" |
| 2 | AI Provider Check | "X Provider verfügbar (LM Studio, Ollama)" | "Kein Provider erreichbar - Degraded Mode" |
| 3 | Vector Store (ChromaDB) | "ChromaDB verbunden - X Dokumente, Y MB" | "ChromaDB Verbindung fehlgeschlagen" |
| 4 | LLM Model Loading | Fortschrittsbalken mit Prozent | "Modell konnte nicht geladen werden: [Fehler]" |
| 5 | Global Knowledge (RAG) | "X Chunks aus globalem Wissen geladen" | "Globales Wissen konnte nicht indexiert werden" |
| 6 | Project Healing | "X Anträge verfügbar" | "Fehler bei Projektstruktur-Reparatur" |

### User Stories zu Anforderung 1:

---

**US-1.1: Startup-Sequenz beim Erstaufruf**

**Ich als** Sachbearbeiter  
**rufe auf** `http://127.0.0.1:8000/` (erstmaliger Aufruf, System noch nicht gestartet)  
**erwarte ich:**
- Startup-Seite wird aufgerufen und angezeigt
- Komponenten werden nacheinander geladen
- Für jede Komponente: Status-Anzeige (Laden → Erfolg/Fehler)
- Model Scanner zeigt Anzahl gefundener Modelle
- Provider Check zeigt verfügbare Provider
- ChromaDB zeigt Verbindungsstatus und Statistiken
- LLM Loading zeigt Fortschrittsbalken
- Global Knowledge zeigt Anzahl geladener Chunks
- Project Healing zeigt Anzahl verfügbarer Anträge
- Nach Abschluss: Automatischer Redirect auf Dashboard -> http://127.0.0.1:8000/

---

**US-1.2: Model Scanner Feedback**

**Ich als** Sachbearbeiter  
**sehe während** der Startup-Sequenz die Komponente "Model Scanner"  
**erwarte ich:**
- Anzeige: "Modelle werden gescannt..."
- Bei Erfolg: "5 Modelle gefunden" (oder entsprechende Anzahl)
- Bei Fehler (keine Modelle): "Kein Modell vorhanden - Bitte installieren Sie ein Modell"
- Bei Fehler (Zugriff): "Modellverzeichnis nicht erreichbar: [Pfad]"

---

**US-1.3: AI Provider Check Feedback**

**Ich als** Sachbearbeiter  
**sehe während** der Startup-Sequenz die Komponente "AI Provider Check"  
**erwarte ich:**
- Prüfung von LM Studio (Port 1234) und Ollama (Port 11434)
- Bei beiden verfügbar: "2 Provider verfügbar (LM Studio bevorzugt)"
- Bei nur Ollama: "1 Provider verfügbar (Ollama)"
- Bei nur LM Studio: "1 Provider verfügbar (LM Studio)"
- Bei keinem: "Kein Provider erreichbar - Degraded Mode aktiv"

---

**US-1.4: Vector Store Feedback**

**Ich als** Sachbearbeiter  
**sehe während** der Startup-Sequenz die Komponente "Vector Store"  
**erwarte ich:**
- Anzeige: "ChromaDB wird initialisiert..."
- Bei Erfolg: "ChromaDB verbunden" mit Zusatzinfos:
  - Anzahl Dokumente
  - Anzahl Chunks
  - Speicherverbrauch in MB
  - Pfad: `data/chromadb`
- Bei Fehler: "ChromaDB Verbindung fehlgeschlagen: [Fehlerdetails]"

---

**US-1.5: LLM Model Loading mit Fortschritt**

**Ich als** Sachbearbeiter  
**sehe während** der Startup-Sequenz die Komponente "LLM Model Loading"  
**erwarte ich:**
- Fortschrittsbalken von 0% bis 100%
- Aktueller Status: "Lade Modell qwen2.5:7b..."
- Bei Erfolg: "Modell geladen ✓"
- Bei Fehler: "Modell konnte nicht geladen werden: [Fehler]"
- Bei Timeout: "Zeitüberschreitung beim Laden des Modells"

---

**US-1.6: Global Knowledge RAG Feedback**

**Ich als** Sachbearbeiter  
**sehe während** der Startup-Sequenz die Komponente "Global Knowledge"  
**erwarte ich:**
- Anzeige: "Globales Wissen wird indexiert..."
- Bei Erfolg: "157 Chunks aus globalem Wissen geladen" (oder aktuelle Anzahl)
- Hinweis welche Dateien indexiert wurden (z.B. guidelines.pdf, herbert.txt)
- Bei leerem Index: "Kein globales Wissen vorhanden - Bitte Dokumente hochladen"
- Bei Fehler: "Indexierung fehlgeschlagen: [Fehler]"

---

**US-1.7: Project Healing Feedback**

**Ich als** Sachbearbeiter  
**sehe während** der Startup-Sequenz die Komponente "Project Healing"  
**erwarte ich:**
- Anzeige: "Projektstruktur wird geprüft..."
- Scan von `data/projects` Ordner
- Bei Erfolg: "12 Anträge verfügbar" (oder aktuelle Anzahl)
- Bei Reparaturen: "3 Anträge repariert, 12 Anträge verfügbar"
- Bei Fehler: "Projektstruktur-Fehler: [Details]"

---

## Anforderung 2: Neustart über Logo-Klick

Ein Klick auf das Logo "IFB Prüfung" (links oben) löst einen vollständigen System-Neustart aus.

### User Stories zu Anforderung 2:

---

**US-2.1: System-Neustart über Logo**

**Ich als** Sachbearbeiter  
**klicke auf** das Logo "IFB Prüfung" (links oben in der Navigation)  
**erwarte ich:**
- Redirect auf `http://localhost:8000/startup?restart=true`
  Über die API kann man über den Endpunkt "startup?restart=true" gehen
- Alle technischen Komponenten werden neu geladen (Cold Start)
- Startup-Sequenz wird vollständig durchgeführt
- Nach Abschluss: Automatischer Redirect auf Dashboard `http://localhost:8000/`

---

**US-2.2: Unterschied Logo vs. Dashboard-Menüpunkt**

**Ich als** Sachbearbeiter  
**unterscheide zwischen:**

| Aktion | URL | Verhalten |
|--------|-----|-----------|
| Klick auf Logo | `/startup?restart=true` | System-Neustart, Startup-Sequenz |
| Klick auf "Dashboard" im Menü | `/` | Direkter Zugriff auf Dashboard (kein Neustart) |

---

## Anforderung 3: Dashboard nur nach erfolgreichem Start

Das Dashboard ist erst verfügbar, wenn die Startup-Sequenz erfolgreich abgeschlossen wurde.

### User Stories zu Anforderung 3:

---

**US-3.1: Dashboard nach erfolgreichem Start**

**Ich als** Sachbearbeiter  
**rufe auf** `http://localhost:8000/` (System bereits gestartet)  
**erwarte ich:**
- Dashboard wird direkt angezeigt
- Kein erneuter Start der Komponenten
- Alle Funktionen sind verfügbar
- Globales Wissen ist bereits geladen

---

**US-3.2: Dashboard-Zugriff vor System-Start**

**Ich als** Sachbearbeiter  
**rufe auf** `http://localhost:8000/` (System noch nicht gestartet)  
**erwarte ich:**
- Redirect auf Startup-Seite
- Startup-Sequenz wird durchgeführt
- Nach Abschluss: Redirect auf Dashboard

---

**US-3.3: Navigation über Dashboard-Menüpunkt**

**Ich als** Sachbearbeiter  
**klicke auf** "Dashboard" im linken Menü (System läuft bereits)  
**erwarte ich:**
- Navigation zu `http://localhost:8000/`
- Dashboard wird angezeigt
- KEIN Neustart des Systems
- Alle Komponenten bleiben geladen

---

## Anforderung 4: Fehlerbehandlung bei Startup

Bei Fehlern während der Startup-Sequenz muss das System angemessen reagieren.

### User Stories zu Anforderung 4:

---

**US-4.1: Teilweiser Start bei Provider-Fehler**

**Ich als** Sachbearbeiter  
**starte das System** wenn kein AI Provider erreichbar ist  
**erwarte ich:**
- Startup-Sequenz läuft weiter
- "Degraded Mode" wird aktiviert
- Warnung wird angezeigt: "Kein AI Provider verfügbar - eingeschränkte Funktionalität"
- Dashboard ist erreichbar, aber Chat/Prüfung deaktiviert

---

**US-4.2: Abbruch bei kritischem Fehler**

**Ich als** Sachbearbeiter  
**starte das System** wenn ChromaDB nicht erreichbar ist  
**erwarte ich:**
- Startup-Sequenz stoppt
- Fehlermeldung: "Kritischer Fehler: Vector Store nicht verfügbar"
- Retry-Button wird angezeigt
- Dashboard ist NICHT erreichbar

---

**US-4.3: Timeout bei LLM-Laden**

**Ich als** Sachbearbeiter  
**starte das System** und das LLM-Laden dauert zu lange  
**erwarte ich:**
- Timeout nach konfigurierter Zeit (z.B. 90 Sekunden)
- Fehlermeldung: "Zeitüberschreitung beim Laden des Modells"
- Option: "Erneut versuchen" oder "Ohne Modell fortfahren"

---

## Anforderung 5: Status-Persistenz

Nach erfolgreichem Start bleibt der System-Status erhalten bis zum expliziten Neustart.

### User Stories zu Anforderung 5:

---

**US-5.1: Seitenwechsel ohne Neustart**

**Ich als** Sachbearbeiter  
**navigiere** zwischen Dashboard → Anträge → Chat → Einstellungen → Dashboard  
**erwarte ich:**
- Kein Neustart der Komponenten
- Alle Daten bleiben geladen
- Schnelle Seitenwechsel

---

**US-5.2: Browser-Refresh ohne Neustart**

**Ich als** Sachbearbeiter  
**drücke F5** auf dem Dashboard (System läuft)  
**erwarte ich:**
- Dashboard lädt neu
- KEIN erneuter System-Start
- Komponenten bleiben aktiv

---

**US-5.3: Expliziter Neustart erforderlich**

**Ich als** Sachbearbeiter  
**möchte** das System neu starten  
**muss ich:**
- Auf das Logo klicken (links oben)
- ODER `http://localhost:8000/startup?restart=true` aufrufen
- Nur diese Aktionen lösen einen Neustart aus

