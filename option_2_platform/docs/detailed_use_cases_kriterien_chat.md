# Detaillierte Use Cases: Kriterienprüfung & Antrags-Chat

**Projekt:** IFB PROFI - KI-gestützte Fördermittelprüfung  
**Version:** 1.0  
**Beispiel-Projekte:** `project/14435678/` und `project/8209d44a/`

---

## Use Case 1: Kriterienprüfung mit annotierten Dateien

### 1.1 Übersicht

Ein Sachbearbeiter möchte automatisch prüfen lassen, ob ein Förderantrag bestimmte Kriterien erfüllt. Das System durchsucht die Antragsdokumente, bewertet jedes Kriterium und erstellt annotierte Dateien mit Markierungen an den Fundstellen.

---

### 1.2 Ausgangssituation

**Projekt-Ordner:** `/data/input/8209d44a/`

```
8209d44a/
├── uploads/
│   ├── IFB_Foerderantrag_Smart_Port_Analytics.pdf
│   ├── Projektskizze_Smart_Port_Analytics.docx
│   └── Kalkulation_2024.xlsx
├── annotated/                      # Leer zu Beginn
├── metadata.json
├── criteria_responses.json         # Leer zu Beginn
└── chat_history.json
```

**Kriterienkatalog:** `/config/criteria_catalog.json`

```
kriterien:
- id: K001
  name: KMU-Prüfung
  kategorie: Formale Voraussetzungen
  kurz: Mind. ein KMU beteiligt
  prompt: >
    Bitte prüfe folgendes Kriterium: Es muss mindestens ein beteiligtes 
    Unternehmen die KMU-Kriterien erfüllen. Prüfe die Anträge ob eine KMU 
    vorhanden ist!
  recommended: true

- id: K002
  name: Hamburger Betriebsstätte
  kategorie: Formale Voraussetzungen
  kurz: Betriebsstätte in Hamburg
  prompt: >
    Prüfe ob der Antragsteller eine Betriebsstätte in Hamburg hat. 
    Suche nach Hamburger Adressen in den Dokumenten.
  recommended: true

- id: K003
  name: EU-Barrierefreiheit
  kategorie: EU-Richtlinien
  kurz: EU-Richtlinie 2019/882
  prompt: >
    Prüfe ob das Vorhaben die Vorgaben der EU-Richtlinie 2019/882 erfüllt 
    (Barrierefreiheitsanforderungen für digitale Produkte).
  recommended: false
```

---

### 1.3 Schritt-für-Schritt Ablauf

#### Schritt 1: Sachbearbeiter öffnet Antrag

**Aktion:** Sachbearbeiter navigiert zu `http://localhost:8000/projects/8209d44a/review`

**System-Reaktion (Backend):**

1. **RAG-Basis laden:**
   ```
   VORHER im RAG: Nur globales Wissen (PROFI-Richtlinie, etc.)
   
   AKTION: Dokumente aus /8209d44a/uploads/ in RAG laden
   - IFB_Foerderantrag_Smart_Port_Analytics.pdf → Chunks erstellen
   - Projektskizze_Smart_Port_Analytics.docx → Chunks erstellen
   - Kalkulation_2024.xlsx → Chunks erstellen
   
   NACHHER im RAG: Globales Wissen + 3 Antragsdokumente
   ```

2. **Docling-Verarbeitung:**
   ```
   Für jedes Dokument:
   - Text extrahieren
   - Struktur erkennen (Seiten, Absätze, Tabellen, Zellen)
   - Chunks mit Metadaten erstellen:
     {
       text: "Hamburg Tech GmbH, Veritaskai 8, 21079 Hamburg-Harburg",
       source: "IFB_Foerderantrag_Smart_Port_Analytics.pdf",
       page: 2,
       paragraph: 4,
       chunk_id: "chunk_0047"
     }
   ```

3. **Status-Update:**
   - `metadata.status` → "in_pruefung"
   - `metadata.geaendert_am` → aktueller Timestamp

**Erwartung Frontend:**
- Dokumentenliste zeigt 3 Dateien
- Kriterien-Panel zeigt alle Kriterien aus Katalog
- Alle Kriterien zeigen Status "Nicht geprüft"

---

#### Schritt 2: Sachbearbeiter startet Kriterienprüfung

**Aktion:** Klick auf "Alle Kriterien prüfen" Button

**System-Reaktion (Backend):**

1. **Queue befüllen:**
   ```
   Queue wird erstellt:
   [
     { queue_id: "q001", antrag_id: "8209d44a", kriterium_id: "K001", status: "pending" },
     { queue_id: "q002", antrag_id: "8209d44a", kriterium_id: "K002", status: "pending" },
     { queue_id: "q003", antrag_id: "8209d44a", kriterium_id: "K003", status: "pending" }
   ]
   ```

2. **RAG-Check:**
   ```
   Prüfung: Sind Dokumente von Antrag 8209d44a im RAG geladen?
   → JA: Weiter mit Prüfung
   → NEIN: Erst laden, dann prüfen
   ```

**Erwartung Frontend:**
- Fortschrittsanzeige: "0 von 3 Kriterien geprüft"
- Button wird deaktiviert

---

#### Schritt 3: Kriterium K001 wird geprüft (KMU-Prüfung)

**System-Reaktion (Backend):**

1. **Prompt zusammenbauen:**

   Aus `config.yaml` → `kriterien_pruefung`:
   ```
   Du bist ein Fördermittelprüfer der IFB Hamburg mit Spezialisierung 
   auf formale Fördervoraussetzungen gemäß PROFI-Richtlinie.
   
   Prüfe das folgende Kriterium gegen die bereitgestellten Dokumente 
   und antworte ausschließlich als JSON im genau folgenden Schema 
   (keine zusätzlichen Texte):
   {
     "status": "rot" | "gelb" | "grün",
     "begruendung": "max 160 Zeichen, kurz und präzise",
     "dokument": "dateiname.pdf",
     "referenz": "Seite X, Absatz Y" | "Zelle XY"
   }
   ```

   Aus `criteria_catalog.json` → K001 `prompt`:
   ```
   Bitte prüfe folgendes Kriterium: Es muss mindestens ein beteiligtes 
   Unternehmen die KMU-Kriterien erfüllen. Prüfe die Anträge ob eine 
   KMU vorhanden ist!
   ```

   **Kombinierter Prompt an LLM:**
   ```
   [kriterien_pruefung aus config.yaml]
   
   [prompt aus criteria_catalog.json für K001]
   ```

2. **RAG-Suche:**
   ```
   Query: "KMU kleine mittlere Unternehmen Mitarbeiter Umsatz"
   
   RAG findet relevante Chunks:
   - Chunk aus IFB_Foerderantrag.pdf, Seite 1: "Hamburg Tech GmbH"
   - Chunk aus IFB_Foerderantrag.pdf, Seite 2: "45 Mitarbeiter, Umsatz 8 Mio EUR"
   - Chunk aus Projektskizze.docx, Seite 1: "KMU gemäß EU-Definition"
   ```

3. **LLM-Verarbeitung:**
   ```
   LLM erhält:
   - System-Prompt (kriterien_pruefung)
   - Kriterium-Prompt (K001)
   - Relevante Chunks aus RAG
   
   LLM analysiert und antwortet.
   ```

4. **LLM-Antwort (Beispiel):**
   ```json
   {
     "status": "grün",
     "begruendung": "Hamburg Tech GmbH erfüllt KMU-Kriterien: 45 MA, 8 Mio EUR Umsatz",
     "dokument": "IFB_Foerderantrag_Smart_Port_Analytics.pdf",
     "referenz": "Seite 2, Absatz 3"
   }
   ```

5. **Antwort validieren:**
   ```
   Prüfung:
   - Ist gültiges JSON? → JA
   - Enthält alle Felder? → JA
   - Status ist rot/gelb/grün? → JA (grün)
   - Begründung ≤ 160 Zeichen? → JA (68 Zeichen)
   
   → Validierung erfolgreich
   ```

6. **Bei ungültiger Antwort (Retry-Logik):**
   ```
   Falls LLM nicht im JSON-Format antwortet:
   
   Retry 1: Erneuter Request mit explizitem Hinweis:
   "Antworte NUR mit dem JSON-Objekt, keine anderen Texte!"
   
   Retry 2: Wenn wieder fehlgeschlagen:
   → Status: "gelb"
   → Begründung: "Keine adäquate Antwort vom Assistenten"
   → Dokument: ""
   → Referenz: ""
   ```

---

#### Schritt 4: Annotierte Datei erstellen

**Auslöser:** Status ist "grün" oder "gelb" UND Dokumentenreferenz vorhanden

**System-Reaktion (Backend):**

1. **Original-Datei identifizieren:**
   ```
   Dokument: "IFB_Foerderantrag_Smart_Port_Analytics.pdf"
   Pfad: /data/input/8209d44a/uploads/IFB_Foerderantrag_Smart_Port_Analytics.pdf
   ```

2. **Fundstelle aus Docling-Metadaten ermitteln:**
   ```
   Referenz: "Seite 2, Absatz 3"
   
   Docling-Mapping:
   - Seite 2 → PDF-Seite 2
   - Absatz 3 → Textblock mit Koordinaten (x1, y1, x2, y2)
   - Text-Snippet: "Hamburg Tech GmbH, 45 Mitarbeiter..."
   ```

3. **Annotierte Datei erstellen:**
   ```
   Aktion:
   1. Original-PDF kopieren
   2. Auf Seite 2 navigieren
   3. Textbereich markieren (Highlight gelb/grün)
   4. Optional: Kommentar hinzufügen "KMU-Kriterium erfüllt (K001)"
   
   Speichern als:
   /data/input/8209d44a/annotated/IFB_Foerderantrag_Smart_Port_Analytics_annotated.pdf
   ```

4. **Für verschiedene Dateitypen:**

   **PDF:**
   ```
   - PyMuPDF zum Markieren verwenden
   - Highlight-Annotation auf Seite/Position
   - Farbe: Grün bei "grün", Gelb bei "gelb"
   ```

   **DOCX:**
   ```
   - python-docx zum Markieren verwenden
   - Text-Highlighting im Absatz
   - Kommentar am Rand optional
   ```

   **XLSX:**
   ```
   - openpyxl zum Markieren verwenden
   - Zellen-Hintergrundfarbe ändern
   - Zelle: "A24" → Zelle A24 markieren
   ```

---

#### Schritt 5: Ergebnis speichern

**System-Reaktion (Backend):**

**criteria_responses.json wird aktualisiert:**

```json
{
  "antrag_id": "8209d44a",
  "pruefungen": [
    {
      "kriterium_id": "K001",
      "kriterium_name": "KMU-Prüfung",
      "status": "grün",
      "begruendung": "Hamburg Tech GmbH erfüllt KMU-Kriterien: 45 MA, 8 Mio EUR Umsatz",
      "geprueft_am": "2026-01-07T14:32:15",
      "evidence": [
        {
          "dokument": "IFB_Foerderantrag_Smart_Port_Analytics.pdf",
          "dokument_original_path": "/uploads/IFB_Foerderantrag_Smart_Port_Analytics.pdf",
          "referenz": "Seite 2, Absatz 3",
          "text_snippet": "Hamburg Tech GmbH, 45 Mitarbeiter, Jahresumsatz 8 Mio EUR",
          "annotated_file": "IFB_Foerderantrag_Smart_Port_Analytics_annotated.pdf",
          "annotated_file_path": "/annotated/IFB_Foerderantrag_Smart_Port_Analytics_annotated.pdf"
        }
      ]
    }
  ]
}
```

---

#### Schritt 6: Nächstes Kriterium (K002) prüfen

**System-Reaktion (Backend):**

1. **RAG-Check:**
   ```
   Antrag 8209d44a noch im RAG? → JA
   → Kein Neuladen erforderlich
   ```

2. **Prompt für K002:**
   ```
   [kriterien_pruefung aus config.yaml]
   
   Prüfe ob der Antragsteller eine Betriebsstätte in Hamburg hat. 
   Suche nach Hamburger Adressen in den Dokumenten.
   ```

3. **LLM-Antwort (Beispiel):**
   ```json
   {
     "status": "grün",
     "begruendung": "Betriebsstätte in Hamburg-Harburg: Veritaskai 8, 21079 Hamburg",
     "dokument": "Projektskizze_Smart_Port_Analytics.docx",
     "referenz": "Seite 1, Absatz 2"
   }
   ```

4. **Annotierte Datei:**
   ```
   Erstellt: /annotated/Projektskizze_Smart_Port_Analytics_annotated.docx
   Markierung: "Veritaskai 8, 21079 Hamburg-Harburg"
   ```

---

#### Schritt 7: Wechsel zu anderem Antrag

**Szenario:** Sachbearbeiter wechselt zu Antrag `14435678`

**System-Reaktion (Backend):**

1. **RAG-Wechsel:**
   ```
   AKTION: Dokumente von 8209d44a aus RAG entfernen
   
   VORHER im RAG:
   - Globales Wissen
   - IFB_Foerderantrag_Smart_Port_Analytics.pdf
   - Projektskizze_Smart_Port_Analytics.docx
   - Kalkulation_2024.xlsx
   
   ENTFERNEN: Alle Chunks mit source aus 8209d44a/uploads/
   
   NACHHER im RAG:
   - Globales Wissen (bleibt!)
   ```

2. **Neue Dokumente laden:**
   ```
   AKTION: Dokumente von 14435678 in RAG laden
   
   Pfad: /data/input/14435678/uploads/
   Dateien:
   - Antrag_MedTech_Innovation.pdf → Chunks erstellen
   - Finanzplan_2025.xlsx → Chunks erstellen
   
   NACHHER im RAG:
   - Globales Wissen
   - Antrag_MedTech_Innovation.pdf
   - Finanzplan_2025.xlsx
   ```

3. **Kriterienprüfung für neuen Antrag:**
   ```
   Queue:
   [
     { antrag_id: "14435678", kriterium_id: "K001", status: "pending" },
     { antrag_id: "14435678", kriterium_id: "K002", status: "pending" },
     ...
   ]
   ```

---

### 1.4 Ordnerstruktur nach Prüfung

**Projekt 8209d44a nach vollständiger Prüfung:**

```
8209d44a/
├── uploads/
│   ├── IFB_Foerderantrag_Smart_Port_Analytics.pdf
│   ├── Projektskizze_Smart_Port_Analytics.docx
│   └── Kalkulation_2024.xlsx
├── annotated/
│   ├── IFB_Foerderantrag_Smart_Port_Analytics_annotated.pdf    # NEU
│   ├── Projektskizze_Smart_Port_Analytics_annotated.docx       # NEU
│   └── Kalkulation_2024_annotated.xlsx                         # NEU (falls Treffer)
├── metadata.json
├── criteria_responses.json    # Enthält alle Prüfergebnisse
└── chat_history.json
```

---

### 1.5 Erwartungen Frontend

| Zustand | Anzeige |
|---------|---------|
| Vor Prüfung | Alle Kriterien: "Nicht geprüft" (grau) |
| Während Prüfung | Fortschrittsbalken, aktives Kriterium markiert |
| Nach Prüfung | Status-Ampel pro Kriterium (🟢🟡🔴) |
| Klick auf Kriterium | Begründung, Dokumentenreferenz (klickbar) |
| Klick auf Referenz | Dokument öffnet sich an markierter Stelle |
| Dokumentenliste | Original + Annotierte Dateien sichtbar |

---

## Use Case 2: Antrags-Chat mit RAG und Quellenverweisen

### 2.1 Übersicht

Ein Sachbearbeiter chattet mit dem KI-Assistenten über einen spezifischen Antrag. Der Assistent nutzt das RAG-System, um Fragen basierend auf den Antragsdokumenten zu beantworten und gibt Quellenverweise an.

---

### 2.2 Ausgangssituation

**Projekt-Ordner:** `/data/input/14435678/`

```
14435678/
├── uploads/
│   ├── Antrag_MedTech_Innovation.pdf
│   ├── Finanzplan_2025.xlsx
│   └── Team_Lebenslaeufe.docx
├── annotated/
├── metadata.json
├── criteria_responses.json
└── chat_history.json              # Leer zu Beginn
```

**Globales Wissen:** `/data/global_knowledge/`

```
global_knowledge/
├── PROFI_Foerderrichtlinie.pdf
├── Leitfaden_Antragsteller.pdf
├── KMU_Definition.pdf
└── ANBest_Nebenbestimmungen.pdf
```

**Config-Prompts:** `/config/config.yaml`

```yaml
prompts:
  begruessung: |
    Willkommen beim IFB PROFI Assistenten. Ich unterstütze Sie bei der 
    Prüfung des Förderantrags. Wie kann ich Ihnen helfen?
    
  global_chat_initial: |
    Du bist ein KI-Assistent der IFB Hamburg namens Herbert.
    Du unterstützt Sachbearbeiter bei der Prüfung von PROFI-Förderanträgen.
    Du hast Zugriff auf die PROFI-Förderrichtlinie und die Antragsdokumente.
    Antworte sachlich, präzise und professionell.
    Beziehe dich auf konkrete Stellen in den Dokumenten.
    
  antrags_chat_initial: |
    Du analysierst den vorliegenden Förderantrag.
    Beantworte Fragen basierend auf den Antragsdokumenten.
    Gib bei jeder Antwort die Quellenreferenz an.
    
  antwort_richtlinie: |
    - Antworte auf Deutsch
    - Maximal 500 Wörter pro Antwort
    - Verwende Fachbegriffe der Förderrichtlinie
    - Gib immer Quellenangaben wenn du aus Dokumenten zitierst
    - Format der Quelle: "Dokument: X, Seite Y" oder "Dokument: X, Zelle Y"
```

---

### 2.3 Schritt-für-Schritt Ablauf

#### Schritt 1: System-Start (einmalig)

**System-Reaktion (Backend):**

1. **Globales Wissen in RAG laden:**
   ```
   Startup-Sequenz:
   
   1. Lade /data/global_knowledge/*.pdf
   2. Verarbeite mit Docling:
      - PROFI_Foerderrichtlinie.pdf → 89 Chunks
      - Leitfaden_Antragsteller.pdf → 45 Chunks
      - KMU_Definition.pdf → 23 Chunks
      - ANBest_Nebenbestimmungen.pdf → 67 Chunks
   3. Speichere in ChromaDB
   
   RAG-Status nach Start:
   - Collection: "ifb_global"
   - Total Chunks: 224
   - Dokumente: 4
   ```

2. **LLM initialisieren:**
   ```
   Provider: Ollama
   Modell: qwen2.5:7b
   Status: Bereit
   ```

**RAG-Inhalt nach Start:**
```
Nur globales Wissen:
- PROFI_Foerderrichtlinie.pdf (89 Chunks)
- Leitfaden_Antragsteller.pdf (45 Chunks)
- KMU_Definition.pdf (23 Chunks)
- ANBest_Nebenbestimmungen.pdf (67 Chunks)
```

---

#### Schritt 2: Sachbearbeiter öffnet Antrag

**Aktion:** Navigation zu `http://localhost:8000/projects/14435678/review`

**System-Reaktion (Backend):**

1. **RAG erweitern um Antragsdokumente:**
   ```
   AKTION: Dokumente aus /14435678/uploads/ hinzufügen
   
   Verarbeitung mit Docling:
   - Antrag_MedTech_Innovation.pdf → 34 Chunks
   - Finanzplan_2025.xlsx → 12 Chunks
   - Team_Lebenslaeufe.docx → 8 Chunks
   
   RAG-Status nachher:
   - Collection: "ifb_global" (224 Chunks) → bleibt
   - Collection: "antrag_14435678" (54 Chunks) → NEU
   
   Oder kombiniert:
   - Globales Wissen: 224 Chunks
   - Antrag 14435678: 54 Chunks
   - Total verfügbar: 278 Chunks
   ```

2. **Chunk-Beispiele aus Antrag:**
   ```json
   {
     "chunk_id": "14435678_chunk_001",
     "text": "MedTech Innovation GmbH, Eppendorfer Weg 123, 20253 Hamburg",
     "source": "Antrag_MedTech_Innovation.pdf",
     "page": 1,
     "paragraph": 2,
     "antrag_id": "14435678"
   },
   {
     "chunk_id": "14435678_chunk_015",
     "text": "Gesamtprojektkosten: 450.000 EUR, Fördersumme beantragt: 250.000 EUR",
     "source": "Finanzplan_2025.xlsx",
     "sheet": "Übersicht",
     "cell": "B12",
     "antrag_id": "14435678"
   }
   ```

**RAG-Inhalt jetzt:**
```
Globales Wissen (immer verfügbar):
- PROFI_Foerderrichtlinie.pdf
- Leitfaden_Antragsteller.pdf
- KMU_Definition.pdf
- ANBest_Nebenbestimmungen.pdf

+ Antragsdokumente (antragsspezifisch):
- Antrag_MedTech_Innovation.pdf
- Finanzplan_2025.xlsx
- Team_Lebenslaeufe.docx
```

---

#### Schritt 3: Neuer Chat wird initialisiert

**Auslöser:** `chat_history.json` ist leer (erster Besuch)

**System-Reaktion (Backend):**

1. **LLM-Context aufbauen:**
   ```
   Schritt 1: System-Prompt senden
   
   AN LLM:
   [global_chat_initial aus config.yaml]
   
   Du bist ein KI-Assistent der IFB Hamburg namens Herbert.
   Du unterstützt Sachbearbeiter bei der Prüfung von PROFI-Förderanträgen.
   ...
   
   [antrags_chat_initial aus config.yaml]
   
   Du analysierst den vorliegenden Förderantrag.
   Beantworte Fragen basierend auf den Antragsdokumenten.
   ...
   
   Wenn du alles verstanden hast, antworte NUR mit dem folgenden Text:
   [begruessung aus config.yaml]
   ```

2. **LLM antwortet:**
   ```
   Willkommen beim IFB PROFI Assistenten. Ich unterstütze Sie bei der 
   Prüfung des Förderantrags. Wie kann ich Ihnen helfen?
   ```

3. **Chat-History initialisieren:**
   
   **chat_history.json wird erstellt:**
   ```json
   {
     "antrag_id": "14435678",
     "messages": [
       {
         "id": "msg_001",
         "role": "system",
         "content": "[global_chat_initial + antrags_chat_initial]",
         "timestamp": "2026-01-07T15:00:00"
       },
       {
         "id": "msg_002",
         "role": "assistant",
         "content": "Willkommen beim IFB PROFI Assistenten. Ich unterstütze Sie bei der Prüfung des Förderantrags. Wie kann ich Ihnen helfen?",
         "timestamp": "2026-01-07T15:00:01",
         "sources": []
       }
     ]
   }
   ```

**Erwartung Frontend:**
- Chat-Bereich zeigt Begrüßung
- Keine Quellenangaben (Begrüßung hat keine)
- Eingabefeld aktiv

---

#### Schritt 4: Sachbearbeiter stellt Frage

**Aktion:** Sachbearbeiter tippt: "Wie hoch ist die beantragte Fördersumme?"

**System-Reaktion (Backend):**

1. **Frage vorbereiten:**
   ```
   User-Frage: "Wie hoch ist die beantragte Fördersumme?"
   
   Intern angehängt (nicht sichtbar für User):
   [antwort_richtlinie aus config.yaml]
   
   Kombinierte Anfrage an LLM:
   "Wie hoch ist die beantragte Fördersumme?
   
   [Antwort-Richtlinie: Antworte auf Deutsch, gib Quellenangaben...]"
   ```

2. **RAG-Suche durchführen:**
   ```
   Query: "Fördersumme beantragt Förderung EUR"
   
   Suche in:
   - Globales Wissen (224 Chunks)
   - Antrag 14435678 (54 Chunks)
   
   Top-K Ergebnisse (k=5):
   
   1. Chunk aus Finanzplan_2025.xlsx (Score: 0.92)
      "Gesamtprojektkosten: 450.000 EUR, Fördersumme beantragt: 250.000 EUR"
      Quelle: Zelle B12
   
   2. Chunk aus Antrag_MedTech_Innovation.pdf (Score: 0.87)
      "Beantragte Zuwendung in Höhe von 250.000 EUR"
      Quelle: Seite 3, Absatz 1
   
   3. Chunk aus PROFI_Foerderrichtlinie.pdf (Score: 0.65)
      "Maximale Förderquote 50% der zuwendungsfähigen Kosten"
      Quelle: Seite 7
   
   4. ...
   ```

3. **LLM-Anfrage mit Kontext:**
   ```
   AN LLM:
   
   [Bisheriger Chat-Verlauf]
   
   [Relevante Chunks aus RAG:]
   ---
   Quelle: Finanzplan_2025.xlsx, Zelle B12
   "Gesamtprojektkosten: 450.000 EUR, Fördersumme beantragt: 250.000 EUR"
   ---
   Quelle: Antrag_MedTech_Innovation.pdf, Seite 3, Absatz 1
   "Beantragte Zuwendung in Höhe von 250.000 EUR"
   ---
   
   [User-Frage:]
   Wie hoch ist die beantragte Fördersumme?
   
   [Antwort-Richtlinie]
   ```

4. **LLM generiert Antwort:**
   ```
   Die beantragte Fördersumme beträgt 250.000 EUR. Dies entspricht 
   bei Gesamtprojektkosten von 450.000 EUR einer Förderquote von 
   etwa 55,5%.
   ```

5. **Quellen extrahieren:**
   ```
   Aus den verwendeten Chunks:
   
   sources: [
     {
       "dokument": "Finanzplan_2025.xlsx",
       "referenz": "Zelle B12"
     },
     {
       "dokument": "Antrag_MedTech_Innovation.pdf", 
       "referenz": "Seite 3, Absatz 1"
     }
   ]
   ```

6. **Chat-History aktualisieren:**
   
   **chat_history.json:**
   ```json
   {
     "antrag_id": "14435678",
     "messages": [
       { "id": "msg_001", "role": "system", "content": "...", "timestamp": "..." },
       { "id": "msg_002", "role": "assistant", "content": "Willkommen...", "timestamp": "...", "sources": [] },
       {
         "id": "msg_003",
         "role": "user",
         "content": "Wie hoch ist die beantragte Fördersumme?",
         "timestamp": "2026-01-07T15:01:30"
       },
       {
         "id": "msg_004",
         "role": "assistant",
         "content": "Die beantragte Fördersumme beträgt 250.000 EUR. Dies entspricht bei Gesamtprojektkosten von 450.000 EUR einer Förderquote von etwa 55,5%.",
         "timestamp": "2026-01-07T15:01:35",
         "sources": [
           {
             "dokument": "Finanzplan_2025.xlsx",
             "referenz": "Zelle B12"
           },
           {
             "dokument": "Antrag_MedTech_Innovation.pdf",
             "referenz": "Seite 3, Absatz 1"
           }
         ]
       }
     ]
   }
   ```

**Erwartung Frontend:**
```
┌─────────────────────────────────────────────────────────┐
│ 🤖 Assistent                                            │
│                                                         │
│ Willkommen beim IFB PROFI Assistenten. Ich unterstütze  │
│ Sie bei der Prüfung des Förderantrags.                  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ 👤 Sie                                                  │
│                                                         │
│ Wie hoch ist die beantragte Fördersumme?                │
│                                                         │
├─────────────────────────────────────────────────────────┤
│ 🤖 Assistent                                            │
│                                                         │
│ Die beantragte Fördersumme beträgt 250.000 EUR. Dies    │
│ entspricht bei Gesamtprojektkosten von 450.000 EUR      │
│ einer Förderquote von etwa 55,5%.                       │
│                                                         │
│ Quellen:                                                │
│ • Finanzplan_2025.xlsx (Zelle B12)          [klickbar]  │
│ • Antrag_MedTech_Innovation.pdf (Seite 3)   [klickbar]  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

#### Schritt 5: Quellenreferenz anklicken

**Aktion:** Sachbearbeiter klickt auf "Finanzplan_2025.xlsx (Zelle B12)"

**System-Reaktion (Frontend):**

1. **Dokument-Viewer öffnen:**
   ```
   Lade: /data/input/14435678/uploads/Finanzplan_2025.xlsx
   ```

2. **Zu Referenz navigieren:**
   ```
   Referenz parsen: "Zelle B12"
   → Sheet: (erstes oder "Übersicht")
   → Zelle: B12
   
   Aktion:
   - Excel-Viewer öffnet Datei
   - Navigiert zu Zelle B12
   - Zelle wird hervorgehoben/markiert
   ```

**Erwartung Frontend:**
- Dokument-Viewer öffnet sich (Modal oder Side-Panel)
- Excel-Datei wird angezeigt
- Zelle B12 ist sichtbar und markiert
- Sachbearbeiter sieht den Kontext der Information

---

#### Schritt 6: Weitere Frage mit globalem Wissen

**Aktion:** Sachbearbeiter fragt: "Wie hoch ist die maximale Förderquote laut Richtlinie?"

**System-Reaktion (Backend):**

1. **RAG-Suche:**
   ```
   Query: "maximale Förderquote Richtlinie Prozent"
   
   Top Ergebnisse:
   
   1. Chunk aus PROFI_Foerderrichtlinie.pdf (Score: 0.94)
      "Die Förderquote beträgt maximal 50% der zuwendungsfähigen Kosten"
      Quelle: Seite 7, Abschnitt 5.2
   
   2. Chunk aus Leitfaden_Antragsteller.pdf (Score: 0.82)
      "Förderquoten variieren je nach Unternehmensgröße: KMU bis 50%"
      Quelle: Seite 12
   ```

2. **LLM-Antwort:**
   ```
   Laut PROFI-Förderrichtlinie beträgt die maximale Förderquote 50% 
   der zuwendungsfähigen Projektkosten. Bei Ihrem Antrag mit einer 
   beantragten Förderung von 250.000 EUR bei 450.000 EUR Gesamtkosten 
   liegt die Quote bei ca. 55,5% und überschreitet damit den maximalen Satz.
   ```

3. **Quellen:**
   ```json
   "sources": [
     {
       "dokument": "PROFI_Foerderrichtlinie.pdf",
       "referenz": "Seite 7, Abschnitt 5.2"
     }
   ]
   ```

**Wichtig:** Diese Antwort kombiniert:
- Globales Wissen (Förderrichtlinie) → "50% Maximum"
- Antragsdokument (Finanzplan) → "250.000 / 450.000 = 55,5%"
- Eigenständige Analyse → "überschreitet Maximum"

---

#### Schritt 7: Existierenden Chat fortsetzen

**Szenario:** Sachbearbeiter schließt Browser, öffnet später wieder

**Aktion:** Navigation zu `http://localhost:8000/projects/14435678/review`

**System-Reaktion (Backend):**

1. **RAG laden:**
   ```
   Prüfung: Welcher Antrag ist aktuell im RAG?
   
   Falls keiner oder anderer Antrag:
   → Alte Antragsdokumente entfernen
   → Dokumente von 14435678 laden
   
   Falls bereits 14435678 geladen:
   → Nichts tun
   ```

2. **Chat-History laden:**
   ```
   Lade: /data/input/14435678/chat_history.json
   
   Inhalt: 4 Messages (system, assistant, user, assistant)
   ```

3. **LLM-Context wiederherstellen:**
   ```
   Context-Window wird befüllt mit:
   - System-Prompt (aus chat_history)
   - Alle bisherigen Nachrichten
   
   LLM "erinnert" sich an vorherige Konversation
   ```

**Erwartung Frontend:**
- Kompletter Chat-Verlauf wird angezeigt
- Alle vorherigen Quellen sind noch klickbar
- KEINE erneute Begrüßung
- Eingabefeld bereit für neue Frage

---

### 2.4 RAG-Wechsel bei Antragswechsel

**Szenario:** Sachbearbeiter wechselt von Antrag `14435678` zu `8209d44a`

**System-Reaktion (Backend):**

```
SCHRITT 1: Erkennen dass anderer Antrag angefordert wird
- Aktuell im RAG: 14435678
- Angefordert: 8209d44a
- → Wechsel erforderlich

SCHRITT 2: Alte Antragsdokumente entfernen
- Entferne alle Chunks mit antrag_id = "14435678"
- Behalte globales Wissen

RAG nach Entfernung:
- PROFI_Foerderrichtlinie.pdf ✓
- Leitfaden_Antragsteller.pdf ✓
- KMU_Definition.pdf ✓
- ANBest_Nebenbestimmungen.pdf ✓
- Antrag_MedTech_Innovation.pdf ✗ (entfernt)
- Finanzplan_2025.xlsx ✗ (entfernt)
- Team_Lebenslaeufe.docx ✗ (entfernt)

SCHRITT 3: Neue Antragsdokumente laden
- Lade Dokumente aus /8209d44a/uploads/
- Erstelle Chunks mit antrag_id = "8209d44a"

RAG nach Laden:
- PROFI_Foerderrichtlinie.pdf ✓
- Leitfaden_Antragsteller.pdf ✓
- KMU_Definition.pdf ✓
- ANBest_Nebenbestimmungen.pdf ✓
- IFB_Foerderantrag_Smart_Port_Analytics.pdf ✓ (neu)
- Projektskizze_Smart_Port_Analytics.docx ✓ (neu)
- Kalkulation_2024.xlsx ✓ (neu)
```

---

### 2.5 Zusammenfassung: Wann wird was geladen?

| Ereignis | RAG-Aktion | LLM-Context |
|----------|------------|-------------|
| System-Start | Globales Wissen laden | Leer |
| Erster Antrag öffnen | + Antragsdokumente | System-Prompt + Begrüßung |
| Chat-Frage stellen | RAG-Suche | + User-Frage + RAG-Chunks |
| Antwort erhalten | - | + Assistenten-Antwort |
| Antrag wechseln | Alte Docs entfernen, neue laden | Neuer Chat oder vorhandener laden |
| Gleichen Antrag erneut öffnen | Nichts (bereits geladen) | Bisherigen Verlauf laden |
| Browser-Refresh | Nichts (RAG persistent) | Chat-History aus JSON laden |

---

## Anhang: Datenfluss-Diagramm

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           SYSTEMSTART                                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  /data/global_knowledge/          ┌──────────────────┐                  │
│  ├── Foerderrichtlinie.pdf  ───▶  │                  │                  │
│  ├── Leitfaden.pdf          ───▶  │    ChromaDB      │                  │
│  └── KMU_Definition.pdf     ───▶  │  (Vector Store)  │                  │
│                                    │                  │                  │
│                                    │  Collection:     │                  │
│                                    │  "ifb_global"    │                  │
│                                    │  224 Chunks      │                  │
│                                    └──────────────────┘                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                        ANTRAG ÖFFNEN (14435678)                         │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  /data/input/14435678/uploads/    ┌──────────────────┐                  │
│  ├── Antrag.pdf             ───▶  │                  │                  │
│  ├── Finanzplan.xlsx        ───▶  │    ChromaDB      │                  │
│  └── Team.docx              ───▶  │                  │                  │
│                                    │  + Collection:   │                  │
│                                    │  "antrag_14435678"│                 │
│                                    │  54 Chunks       │                  │
│                                    │                  │                  │
│                                    │  TOTAL: 278      │                  │
│                                    └──────────────────┘                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                           CHAT-FRAGE                                     │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│  User: "Wie hoch ist die Fördersumme?"                                  │
│                                     │                                    │
│                                     ▼                                    │
│                          ┌──────────────────┐                           │
│                          │   RAG-Suche      │                           │
│                          │                  │                           │
│                          │ Query → Embedding│                           │
│                          │ → Similarity     │                           │
│                          │ → Top-K Chunks   │                           │
│                          └──────────────────┘                           │
│                                     │                                    │
│                                     ▼                                    │
│                          ┌──────────────────┐                           │
│                          │      LLM         │                           │
│                          │                  │                           │
│                          │ Context:         │                           │
│                          │ - Chat-History   │                           │
│                          │ - RAG-Chunks     │                           │
│                          │ - User-Frage     │                           │
│                          │ - Richtlinie     │                           │
│                          └──────────────────┘                           │
│                                     │                                    │
│                                     ▼                                    │
│                          ┌──────────────────┐                           │
│                          │    Antwort       │                           │
│                          │                  │                           │
│                          │ Text + Quellen   │                           │
│                          │                  │                           │
│                          └──────────────────┘                           │
│                                     │                                    │
│                                     ▼                                    │
│                          /data/input/14435678/                          │
│                          chat_history.json                              │
│                          (persistiert)                                  │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```
