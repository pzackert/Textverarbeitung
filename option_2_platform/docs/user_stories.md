# User Stories: IFB PROFI Antragsverarbeitung

**Projekt:** IFB PROFI - KI-gestützte Fördermittelprüfung  
**Version:** 1.0  
**Datum:** 02.01.2026

---

## Inhaltsverzeichnis

1. [Systemstart](#1-systemstart)
2. [Globaler Chat](#2-globaler-chat)
3. [Antragsverwaltung](#3-antragsverwaltung)
4. [Antrags-Chat](#4-antrags-chat)
5. [Kriterienprüfung](#5-kriterienprüfung)
6. [Dokumentenverwaltung](#6-dokumentenverwaltung)

---

## 1. Systemstart

### US-1.1: System starten

**Ich als** Sachbearbeiter  
**möchte** das System starten  
**um** mit der Antragsbearbeitung beginnen zu können

**Vorbedingungen:**
- Keine

**Systemzustand nach Start:**
- Engine ist initialisiert
- LLM-Provider (Ollama/LM Studio) ist gestartet und erreichbar
- RAG-System ist initialisiert
- Webservice läuft auf `http://localhost:8000`

**RAG-Inhalt nach Start:**
- Globales Wissen aus `/data/global_knowledge/` ist geladen
- Alle PDF, DOCX, XLSX Dateien aus diesem Ordner sind im RAG verfügbar
- Keine antragsspezifischen Dokumente geladen

**LLM-Context nach Start:**
- Kein Chat-Context geladen
- LLM ist bereit für neue Anfragen

**Erwartetes Ergebnis:**
- System ist vollständig betriebsbereit
- Frontend kann Status aller Komponenten abfragen
- Globales Wissen steht für alle Chats zur Verfügung

---

## 2. Globaler Chat

### US-2.1: Neuen globalen Chat starten

**Ich als** Sachbearbeiter  
**öffne** die Seite `http://localhost:8000/chat`  
**um** einen neuen Chat mit dem KI-Assistenten zu beginnen

**Vorbedingungen:**
- System ist gestartet (US-1.1 erfüllt)
- Globales Wissen ist im RAG geladen

**RAG-Inhalt:**
- NUR globales Wissen aus `/data/global_knowledge/`
- Keine antragsspezifischen Dokumente

**LLM-Context wird aufgebaut:**
1. System sendet `global_chat_initial` (aus config.yaml) an LLM
2. LLM versteht seine Rolle als IFB-Assistent
3. LLM antwortet mit exaktem Text aus `begruessung` (config.yaml)

**Dateien werden angelegt:**
- Neue Chat-Datei: `/data/chats/chat_{timestamp}_{uuid}.json`
- Inhalt: System-Prompt und Begrüßung werden gespeichert

**Erwartetes Ergebnis:**
- Chat-Fenster öffnet sich
- Begrüßungsnachricht vom Assistenten wird angezeigt
- Eingabefeld ist aktiv
- KEINE Quellenangaben bei Antworten

---

### US-2.2: Existierenden globalen Chat fortsetzen

**Ich als** Sachbearbeiter  
**öffne** einen existierenden Chat aus der Chat-Liste  
**um** eine frühere Konversation fortzusetzen

**Vorbedingungen:**
- System ist gestartet (US-1.1 erfüllt)
- Chat-Datei existiert: `/data/chats/{chat_id}.json`

**RAG-Inhalt:**
- NUR globales Wissen aus `/data/global_knowledge/`

**LLM-Context wird aufgebaut:**
1. Gesamter Chat-Verlauf aus JSON wird geladen
2. `global_chat_initial` ist bereits im Verlauf enthalten
3. Alle bisherigen Fragen und Antworten sind im Context

**Erwartetes Ergebnis:**
- Kompletter Chat-Verlauf wird angezeigt
- KEINE erneute Begrüßung
- Eingabefeld ist aktiv
- Assistent "erinnert" sich an vorherige Konversation

---

### US-2.3: Frage im globalen Chat stellen

**Ich als** Sachbearbeiter  
**stelle** eine Frage im globalen Chat (z.B. "Was sind die Fördervoraussetzungen für KMU?")  
**um** Informationen vom KI-Assistenten zu erhalten

**Vorbedingungen:**
- Globaler Chat ist geöffnet (US-2.1 oder US-2.2)
- RAG enthält globales Wissen

**RAG-Inhalt:**
- Globales Wissen (PROFI-Richtlinie, Leitfäden, etc.)

**LLM-Context enthält:**
- `global_chat_initial` (Rollendefinition)
- Bisheriger Chat-Verlauf
- Meine neue Frage
- `antwort_richtlinie` (wird intern angehängt, nicht sichtbar)

**Ablauf:**
1. Meine Frage wird im Chat angezeigt
2. System zeigt Lade-Indikator
3. Frage + `antwort_richtlinie` wird an LLM gesendet
4. LLM nutzt RAG für Antwort
5. Antwort wird angezeigt

**Dateien werden aktualisiert:**
- `/data/chats/{chat_id}.json` wird um Frage und Antwort ergänzt

**Erwartetes Ergebnis:**
- Antwort vom Assistenten wird angezeigt
- OHNE Quellenangaben (anders als bei Antrags-Chat!)
- Chat-Verlauf ist persistiert

---

### US-2.4: Globalen Chat löschen

**Ich als** Sachbearbeiter  
**lösche** einen globalen Chat  
**um** nicht mehr benötigte Konversationen zu entfernen

**Vorbedingungen:**
- Chat existiert in `/data/chats/`

**Ablauf:**
1. Ich klicke auf "Chat löschen"
2. Bestätigungsdialog erscheint
3. Ich bestätige

**Dateien werden gelöscht:**
- `/data/chats/{chat_id}.json` wird gelöscht

**Erwartetes Ergebnis:**
- Chat ist aus der Liste entfernt
- Datei ist vom Dateisystem gelöscht
- Keine Wiederherstellung möglich

---

## 3. Antragsverwaltung

### US-3.1: Antragsübersicht öffnen

**Ich als** Sachbearbeiter  
**öffne** die Seite `http://localhost:8000/projects`  
**um** alle Förderanträge zu sehen

**Vorbedingungen:**
- System ist gestartet (US-1.1 erfüllt)

**Systemverhalten:**
1. System scannt `/data/input/` Ordner
2. Jeder Unterordner = ein Antrag
3. Für jeden Ordner wird `metadata.json` gelesen
4. Tabelle wird mit allen Anträgen befüllt

**RAG-Inhalt:**
- Nur globales Wissen (keine Antragsdokumente)

**Erwartetes Ergebnis:**
- Tabelle zeigt alle Anträge mit:
  - Antragsnummer (= Ordnername)
  - Projektname
  - Antragsteller
  - Fördersumme
  - Status (Entwurf/In Prüfung/Abgeschlossen)
  - Anzahl Dokumente (nur aus `/uploads/`)
  - Letzte Änderung
  - Aktionen (Öffnen, Löschen, Prüfen)

---

### US-3.2: Neuen Antrag anlegen

**Ich als** Sachbearbeiter  
**erstelle** einen neuen Antrag über den Dialog  
**um** einen Förderantrag im System zu erfassen

**Vorbedingungen:**
- Antragsübersicht ist geöffnet (US-3.1)

**Eingabedaten:**
- Projektname (Pflicht)
- Antragsteller (Pflicht)
- Fördersumme (Pflicht)
- Beschreibung (optional)

**Ordnerstruktur wird angelegt:**
```
/data/input/{neue_id}/
├── uploads/                    # Leer, für Dokumente
├── annotated/                  # Leer, für annotierte Dateien
├── metadata.json               # Mit eingegebenen Daten
├── criteria_responses.json     # Leer initialisiert
└── chat_history.json           # Leer initialisiert
```

**metadata.json enthält:**
```json
{
  "id": "{neue_id}",
  "projektname": "{eingabe}",
  "antragsteller": "{eingabe}",
  "foerdersumme": {eingabe},
  "beschreibung": "{eingabe}",
  "status": "entwurf",
  "erstellt_am": "{timestamp}",
  "geaendert_am": "{timestamp}"
}
```

**criteria_responses.json enthält:**
```json
{
  "antrag_id": "{neue_id}",
  "pruefungen": []
}
```

**chat_history.json enthält:**
```json
{
  "antrag_id": "{neue_id}",
  "messages": []
}
```

**Erwartetes Ergebnis:**
- Neuer Antrag erscheint in der Tabelle
- Status ist "Entwurf"
- Dokumentenanzahl ist 0
- Alle JSON-Dateien sind korrekt initialisiert

---

### US-3.3: Antrag manuell anlegen (ohne Frontend)

**Ich als** Sachbearbeiter  
**erstelle** manuell einen Ordner mit Dokumenten in `/data/input/`  
**um** einen Antrag ohne Frontend-Dialog zu importieren

**Vorbedingungen:**
- Ich habe Zugriff auf das Dateisystem

**Meine Aktion:**
- Ordner erstellen: `/data/input/{mein_ordnername}/`
- Unterordner erstellen: `/data/input/{mein_ordnername}/uploads/`
- Dokumente in `uploads/` ablegen

**Systemverhalten beim nächsten Start/Scan:**
1. System findet neuen Ordner
2. Prüft: Existiert `uploads/` Ordner? → Ja
3. Prüft: Existiert `metadata.json`? → Nein
4. System erstellt automatisch alle fehlenden Dateien:
   - `metadata.json` (mit ID aus Ordnername, Rest leer)
   - `criteria_responses.json` (leer)
   - `chat_history.json` (leer)
   - `annotated/` Ordner

**Erwartetes Ergebnis:**
- Antrag erscheint in der Übersicht
- Dokumentenanzahl entspricht Dateien in `uploads/`
- Status ist "Entwurf"
- Ich kann den Antrag normal bearbeiten

---

### US-3.4: Antrag öffnen

**Ich als** Sachbearbeiter  
**öffne** einen Antrag durch Klick auf "Öffnen"  
**um** den Antrag zu bearbeiten

**Vorbedingungen:**
- Antrag existiert in `/data/input/{antrag_id}/`

**Navigation:**
- Von `http://localhost:8000/projects`
- Nach `http://localhost:8000/projects/{antrag_id}/review`

**RAG wird aktualisiert:**
1. Falls anderer Antrag im RAG: Dessen Dokumente entfernen
2. Dokumente aus `/data/input/{antrag_id}/uploads/` laden
3. Globales Wissen bleibt erhalten

**RAG-Inhalt nach Öffnen:**
- Globales Wissen (immer vorhanden)
- PLUS alle Dokumente aus `uploads/` dieses Antrags

**Status wird aktualisiert:**
- Falls Status war "entwurf" → wird zu "in_pruefung"
- `geaendert_am` wird aktualisiert

**Erwartetes Ergebnis:**
- Antragsansicht öffnet sich
- Dokumentenliste zeigt alle Dateien
- Chat ist verfügbar
- Kriterienprüfung ist verfügbar

---

### US-3.5: Antrag löschen

**Ich als** Sachbearbeiter  
**lösche** einen Antrag  
**um** nicht mehr benötigte Anträge zu entfernen

**Vorbedingungen:**
- Antrag existiert in `/data/input/{antrag_id}/`

**Ablauf:**
1. Ich klicke auf "Löschen"
2. Bestätigungsdialog erscheint
3. Ich bestätige

**Ordner wird gelöscht:**
- Gesamter Ordner `/data/input/{antrag_id}/` wird gelöscht
- Inkl. alle Unterordner und Dateien
- `uploads/`, `annotated/`, alle JSON-Dateien

**RAG wird aktualisiert:**
- Falls dieser Antrag im RAG geladen war: Dokumente entfernen

**Erwartetes Ergebnis:**
- Antrag ist aus der Übersicht entfernt
- Ordner ist vom Dateisystem gelöscht
- Keine Wiederherstellung möglich

---

## 4. Antrags-Chat

### US-4.1: Neuen Antrags-Chat starten

**Ich als** Sachbearbeiter  
**öffne** einen Antrag zum ersten Mal  
**um** mit dem KI-Assistenten über diesen Antrag zu chatten

**Vorbedingungen:**
- Antrag existiert
- `chat_history.json` ist leer (keine bisherigen Nachrichten)

**RAG-Inhalt:**
- Globales Wissen aus `/data/global_knowledge/`
- PLUS Antragsdokumente aus `/data/input/{antrag_id}/uploads/`

**LLM-Context wird aufgebaut:**
1. System sendet `global_chat_initial` (aus config.yaml) an LLM
2. LLM versteht seine Rolle als IFB-Assistent
3. LLM hat Zugriff auf Antragsdokumente via RAG
4. LLM antwortet mit exaktem Text aus `begruessung` (config.yaml)

**Dateien werden aktualisiert:**
- `/data/input/{antrag_id}/chat_history.json` wird mit System-Prompt und Begrüßung befüllt

**Erwartetes Ergebnis:**
- Chat-Bereich zeigt Begrüßung
- Eingabefeld ist aktiv
- Quellenangaben werden bei Antworten angezeigt (Unterschied zu globalem Chat!)

---

### US-4.2: Existierenden Antrags-Chat fortsetzen

**Ich als** Sachbearbeiter  
**öffne** einen Antrag erneut  
**um** eine frühere Konversation zu diesem Antrag fortzusetzen

**Vorbedingungen:**
- Antrag existiert
- `chat_history.json` enthält bisherige Nachrichten

**RAG-Inhalt:**
- Globales Wissen
- PLUS Antragsdokumente (müssen ggf. neu geladen werden)

**LLM-Context wird aufgebaut:**
1. Gesamter Chat-Verlauf aus `chat_history.json` wird geladen
2. `global_chat_initial` ist bereits im Verlauf enthalten
3. Alle bisherigen Fragen und Antworten sind im Context

**Erwartetes Ergebnis:**
- Kompletter Chat-Verlauf wird angezeigt
- KEINE erneute Begrüßung
- Eingabefeld ist aktiv
- Assistent "erinnert" sich an vorherige Konversation zu diesem Antrag

---

### US-4.3: Frage zum Antrag stellen

**Ich als** Sachbearbeiter  
**stelle** eine Frage zum Antrag (z.B. "Ist der Antragsteller eine KMU?")  
**um** Informationen aus den Antragsdokumenten zu erhalten

**Vorbedingungen:**
- Antrags-Chat ist geöffnet (US-4.1 oder US-4.2)
- RAG enthält Antragsdokumente

**RAG-Inhalt:**
- Globales Wissen (PROFI-Richtlinie, etc.)
- Antragsdokumente (z.B. IFB_Foerderantrag.pdf, Projektskizze.docx)

**LLM-Context enthält:**
- `global_chat_initial` (Rollendefinition)
- Bisheriger Chat-Verlauf zu diesem Antrag
- Meine neue Frage
- `antwort_richtlinie` (wird intern angehängt, nicht sichtbar)

**Ablauf:**
1. Meine Frage wird im Chat angezeigt
2. System zeigt Lade-Indikator
3. Frage + `antwort_richtlinie` wird an LLM gesendet
4. LLM nutzt RAG (durchsucht Antragsdokumente)
5. LLM generiert Antwort MIT Quellenangaben
6. Antwort wird angezeigt

**Dateien werden aktualisiert:**
- `/data/input/{antrag_id}/chat_history.json` wird um Frage, Antwort und Quellen ergänzt

**Erwartetes Ergebnis:**
- Antwort vom Assistenten wird angezeigt
- MIT Quellenangaben darunter:
  ```
  Quellen:
  - IFB_Foerderantrag.pdf (Seite 2, Absatz 4)
  ```
- Quellen sind klickbar → öffnen Dokument an der Stelle

---

### US-4.4: Quellenreferenz öffnen

**Ich als** Sachbearbeiter  
**klicke** auf eine Quellenangabe (z.B. "IFB_Foerderantrag.pdf (Seite 2, Absatz 4)")  
**um** die genaue Fundstelle im Dokument zu sehen

**Vorbedingungen:**
- Antwort mit Quellenangabe ist vorhanden
- Dokument existiert in `/uploads/`

**Ablauf:**
1. Ich klicke auf die Quellenangabe
2. Dokument-Viewer öffnet sich
3. Dokument wird geladen
4. Viewer navigiert zu Seite 2
5. Optional: Absatz 4 wird hervorgehoben

**Referenz-Formate (von Docling):**
- "Seite 3, Absatz 2" → PDF/DOCX öffnet auf Seite 3
- "Zelle A24" → XLSX öffnet mit Fokus auf Zelle A24

**Erwartetes Ergebnis:**
- Dokument ist geöffnet
- Ich sehe die exakte Stelle, auf die sich die Antwort bezieht

---

## 5. Kriterienprüfung

### US-5.1: Kriterienkatalog ansehen

**Ich als** Sachbearbeiter  
**sehe** den Kriterienkatalog in der Antragsansicht  
**um** zu wissen, welche Kriterien geprüft werden können

**Vorbedingungen:**
- Antrag ist geöffnet (US-3.4)

**Datenquelle:**
- `/config/criteria_catalog.json`

**Anzeige pro Kriterium:**
- ID (K001, K002, ...)
- Name
- Kategorie
- Kurzbeschreibung
- Status der Prüfung (falls bereits geprüft)
- Recommended-Flag (Pflicht oder optional)

**Erwartetes Ergebnis:**
- Alle definierten Kriterien sind sichtbar
- Bereits geprüfte Kriterien zeigen Status (Grün/Gelb/Rot)
- Noch nicht geprüfte Kriterien zeigen "Nicht geprüft"

---

### US-5.2: Einzelnes Kriterium prüfen

**Ich als** Sachbearbeiter  
**klicke** auf "Prüfen" bei einem Kriterium (z.B. K001 - KMU-Prüfung)  
**um** dieses Kriterium automatisch prüfen zu lassen

**Vorbedingungen:**
- Antrag ist geöffnet
- RAG enthält Antragsdokumente

**RAG-Inhalt muss sein:**
- Globales Wissen
- Antragsdokumente aus `/data/input/{antrag_id}/uploads/`

**LLM erhält folgenden Prompt:**
```
{kriterien_pruefung aus config.yaml}

{prompt aus criteria_catalog.json für K001}
```

**Konkret für K001:**
```
Du bist ein Fördermittelprüfer der IFB Hamburg mit Spezialisierung auf formale Fördervoraussetzungen gemäß PROFI-Richtlinie.

Gib als Antwort/Response als JSON zurück:
{
  "status": "rot" | "gelb" | "grün",
  "begruendung": "",
  "dokument": "projektantrag.pdf",
  "referenz": "Seite 3, Absatz 3" | "Zelle A24"
}

Bitte prüfe folgendes Kriterium: Es muss mind. ein beteiligtes gültiges Unternehmen einer KMU sein. Prüfe die Anträge ob eine KMU vorhanden ist!
```

**Ablauf:**
1. Prüfung wird in Queue gelegt
2. UI zeigt "In Queue..." oder Lade-Indikator
3. Backend verarbeitet (LLM prüft mit RAG)
4. LLM antwortet im JSON-Format
5. Ergebnis wird validiert
6. Bei ungültigem Format: Retry mit Hinweis
7. Ergebnis wird gespeichert

**Dateien werden aktualisiert:**
- `/data/input/{antrag_id}/criteria_responses.json` wird um Ergebnis ergänzt

**LLM-Antwort (Beispiel):**
```json
{
  "status": "grün",
  "begruendung": "Hamburg Tech GmbH ist als KMU im Handelsregister eingetragen.",
  "dokument": "IFB_Foerderantrag.pdf",
  "referenz": "Seite 2, Absatz 4"
}
```

**Erwartetes Ergebnis:**
- Kriterium zeigt Status-Ampel (🟢 Grün)
- Begründung ist sichtbar
- Dokumentenreferenz ist klickbar

---

### US-5.3: Alle Kriterien für Antrag prüfen

**Ich als** Sachbearbeiter  
**klicke** auf "Alle Kriterien prüfen"  
**um** alle Kriterien für diesen Antrag automatisch prüfen zu lassen

**Vorbedingungen:**
- Antrag ist geöffnet
- RAG enthält Antragsdokumente

**RAG-Inhalt:**
- Bleibt konstant während gesamter Prüfung
- Globales Wissen + Antragsdokumente

**LLM-Context pro Kriterium:**
- Jedes Kriterium wird separat geprüft
- Für jedes Kriterium: `kriterien_pruefung` + jeweiliger `prompt`
- Keine Abhängigkeiten zwischen Prüfungen

**Queue-Verarbeitung:**
```
Antrag 8209d44a + K001 → In Queue
Antrag 8209d44a + K002 → In Queue
Antrag 8209d44a + K003 → In Queue
...
```

**Ablauf:**
1. Alle Kriterien werden in Queue gelegt
2. UI zeigt Fortschritt (z.B. "3 von 10 geprüft")
3. Ergebnisse werden sukzessive angezeigt
4. Nach Abschluss: Alle Kriterien haben Status

**Erwartetes Ergebnis:**
- Alle Kriterien zeigen Status-Ampel
- Fortschritt ist während Prüfung sichtbar
- Keine Blockierung der UI

---

### US-5.4: Kriterium erneut prüfen

**Ich als** Sachbearbeiter  
**klicke** auf "Erneut prüfen" bei einem bereits geprüften Kriterium  
**um** die Prüfung mit möglicherweise aktualisierten Dokumenten zu wiederholen

**Vorbedingungen:**
- Kriterium wurde bereits geprüft
- Altes Ergebnis ist vorhanden

**Ablauf:**
- Identisch zu US-5.2
- Altes Ergebnis wird überschrieben

**Erwartetes Ergebnis:**
- Neues Ergebnis ersetzt altes
- Neuer Timestamp
- Ggf. neue annotierte Datei

---

### US-5.5: Alle Anträge prüfen (Batch)

**Ich als** Sachbearbeiter  
**starte** die Prüfung aller Kriterien für alle Anträge  
**um** eine Massenprüfung durchzuführen

**Vorbedingungen:**
- Mehrere Anträge existieren

**RAG-Wechsel bei Antragswechsel:**
```
Antrag 123 + K001 → RAG: Antrag 123 laden → Prüfen → Speichern
Antrag 123 + K002 → RAG: bereits geladen → Prüfen → Speichern
Antrag 123 + K003 → RAG: bereits geladen → Prüfen → Speichern
Antrag 999 + K001 → RAG: Antrag 999 laden (123 entfernen!) → Prüfen → Speichern
Antrag 999 + K002 → RAG: bereits geladen → Prüfen → Speichern
```

**Queue-Verarbeitung:**
- Sequenziell, nicht parallel
- RAG wird nur bei Antragswechsel neu geladen
- Optimiert für Performance

**Erwartetes Ergebnis:**
- Alle Anträge haben alle Kriterien geprüft
- Fortschritt ist sichtbar
- Kann längere Zeit dauern

---

### US-5.6: Annotierte Datei wird erstellt

**Ich als** Sachbearbeiter  
**sehe** nach einer Kriterienprüfung eine annotierte Datei  
**um** die Fundstelle visuell markiert zu haben

**Vorbedingungen:**
- Kriterienprüfung ist abgeschlossen
- Status ist "grün" oder "gelb"
- Dokumentenreferenz ist vorhanden

**Systemverhalten:**
1. Originaldatei wird aus `/uploads/` kopiert
2. Kopie erhält Suffix `_annotated`
3. Fundstelle wird im Dokument markiert (Highlighting)
4. Datei wird in `/annotated/` gespeichert

**Dateien werden angelegt:**
```
Original: /uploads/IFB_Foerderantrag.pdf
Annotiert: /annotated/IFB_Foerderantrag_annotated.pdf
```

**criteria_responses.json enthält:**
```json
{
  "evidence": [
    {
      "dokument": "IFB_Foerderantrag.pdf",
      "dokument_original_path": "/uploads/IFB_Foerderantrag.pdf",
      "referenz": "Seite 2, Absatz 4",
      "text_snippet": "Hamburg Tech GmbH, gegründet 2018",
      "annotated_file": "IFB_Foerderantrag_annotated.pdf",
      "annotated_file_path": "/annotated/IFB_Foerderantrag_annotated.pdf"
    }
  ]
}
```

**Erwartetes Ergebnis:**
- Annotierte Datei erscheint in Dokumentenliste
- Visuell als "Annotiert" gekennzeichnet
- Öffnen zeigt Markierung an der Fundstelle

---

## 6. Dokumentenverwaltung

### US-6.1: Dokumente zum Antrag hochladen

**Ich als** Sachbearbeiter  
**lade** ein Dokument zum Antrag hoch  
**um** weitere Unterlagen zur Prüfung hinzuzufügen

**Vorbedingungen:**
- Antrag ist geöffnet

**Erlaubte Dateitypen:**
- PDF
- DOCX
- XLSX

**Ablauf:**
1. Ich klicke auf "Hochladen"
2. Datei-Dialog öffnet sich
3. Ich wähle Datei(en) aus
4. Upload startet
5. Datei wird in `/data/input/{antrag_id}/uploads/` gespeichert

**RAG wird aktualisiert:**
- Neue Datei wird zum RAG hinzugefügt
- Sofort für Fragen und Prüfungen verfügbar

**Erwartetes Ergebnis:**
- Datei erscheint in Dokumentenliste
- Dokumentenanzahl in Übersicht erhöht sich
- RAG kann neue Datei durchsuchen

---

### US-6.2: Dokument öffnen

**Ich als** Sachbearbeiter  
**öffne** ein Dokument aus der Liste  
**um** den Inhalt einzusehen

**Vorbedingungen:**
- Dokument existiert in `/uploads/` oder `/annotated/`

**Ablauf:**
1. Ich klicke auf Dokumentname
2. Dokument-Viewer öffnet sich
3. Inhalt wird angezeigt

**Erwartetes Ergebnis:**
- Dokument ist lesbar
- Bei annotierten Dokumenten: Markierungen sichtbar
- Navigation im Dokument möglich

---

### US-6.3: Original vs. Annotiert unterscheiden

**Ich als** Sachbearbeiter  
**sehe** in der Dokumentenliste den Unterschied zwischen Original und annotierter Version  
**um** zu wissen, welches Dokument Markierungen enthält

**Anzeige:**
| Dokument | Typ |
|----------|-----|
| IFB_Foerderantrag.pdf | Original |
| IFB_Foerderantrag_annotated.pdf | Annotiert |
| Projektskizze.docx | Original |

**Kennzeichnung:**
- Original: Normales Datei-Icon
- Annotiert: Icon mit Markierungs-Symbol ODER Label "Annotiert"

**Erwartetes Ergebnis:**
- Klare visuelle Unterscheidung
- Ich kann gezielt Original oder annotierte Version öffnen

---

## Anhang: Zusammenfassung RAG-Zustände

| Kontext | RAG enthält |
|---------|-------------|
| Nach Systemstart | Nur globales Wissen |
| Globaler Chat | Nur globales Wissen |
| Antrag geöffnet | Globales Wissen + Antragsdokumente |
| Antragswechsel | Alte Antragsdocs entfernen + Neue laden |
| Kriterienprüfung | Muss Antragsdokumente enthalten |

---

## Anhang: Zusammenfassung LLM-Context

| Kontext | LLM erhält |
|---------|------------|
| Neuer globaler Chat | `global_chat_initial` → Antwort: `begruessung` |
| Existierender globaler Chat | Gesamter Chat-Verlauf |
| Frage im globalen Chat | Frage + `antwort_richtlinie` |
| Neuer Antrags-Chat | `global_chat_initial` → Antwort: `begruessung` |
| Frage im Antrags-Chat | Frage + `antwort_richtlinie` + Quellen |
| Kriterienprüfung | `kriterien_pruefung` + `prompt` vom Kriterium |

---

## Anhang: Konfigurationswerte (config.yaml)

```yaml
global_chat_initial: |
  Du bist ein KI-Assistent der IFB Hamburg...
  
begruessung: |
  Willkommen beim IFB PROFI Assistenten...
  
antwort_richtlinie: |
  Antworte sachlich, präzise und professionell...
  
kriterien_pruefung: |
  Du bist ein Fördermittelprüfer der IFB Hamburg...
  Gib als Antwort/Response als JSON zurück:
  {
    "status": "rot" | "gelb" | "grün",
    "begruendung": "",
    "dokument": "...",
    "referenz": "..."
  }
```
