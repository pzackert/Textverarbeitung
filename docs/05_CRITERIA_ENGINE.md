# Criteria Engine
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 2.0 (Option 1 - Super-Lite)  
**Stand:** 13. November 2025

## Übersicht

System zur Definition und Prüfung von Förderkriterien. Insgesamt werden **6 Kriterien** geprüft.

**Für Option 1 (Super-Lite):**
- Iterative Prüfung (ein Kriterium nach dem anderen)
- Einfache JSON-basierte Prompts
- RAG-Context aus ChromaDB oder LM Studio
- Strukturierte JSON-Antworten vom LLM
- Speicherung als JSON-Files

---

### Kriterium 1: Projektort
**Ziel:** Betriebsstätte in Hamburg (oder Umgebung)
**Typ:** Boolean
**Erforderlich:** Ja

**Prompt:**
```
Prüfe anhand der vorliegenden Dokumente, ob das antragstellende Unternehmen 
eine Betriebsstätte in Hamburg oder im Hamburger Umland hat.

Suche nach:
- Handelsregisterauszug mit Hamburg-Adresse
- Firmenadresse in Hamburg
- Betriebsstätte in Hamburg

Antworte im Format:
{
    "erfuellt": true/false,
    "ort": "gefundener Standort",
    "begruendung": "...",
    "quelle": "Dokument + Seite"
}
```

### Kriterium 2: Unternehmensalter
**Ziel:** Unternehmen muss gegründet sein
**Typ:** Boolean
**Erforderlich:** Ja

**Prompt:**
```
Prüfe das Alter des Unternehmens anhand des Handelsregisterauszugs oder 
der Unternehmensbeschreibung.

Ermittle:
- Gründungsdatum
- Registrierungsdatum

Antworte im Format:
{
    "erfuellt": true/false,
    "gruendungsdatum": "YYYY-MM-DD",
    "alter_in_jahren": number,
    "begruendung": "...",
    "quelle": "Dokument + Seite"
}
```

### Kriterium 3: Projektbeginn
**Ziel:** Projekt darf noch nicht begonnen haben (vor Bewilligung)
**Typ:** Boolean
**Erforderlich:** Ja

**Prompt:**
```
Prüfe, ob das Projekt bereits begonnen hat oder noch nicht gestartet ist.

Vor Bewilligung darf NICHT mit dem Projekt begonnen worden sein.

Suche nach:
- Geplanter Projektbeginn (Datum)
- Hinweise auf bereits begonnene Arbeiten
- Projektlaufzeit

Antworte im Format:
{
    "erfuellt": true/false,
    "projektbeginn": "YYYY-MM-DD",
    "bereits_begonnen": true/false,
    "begruendung": "...",
    "quelle": "Dokument + Seite"
}
```

### Kriterium 4: Projektziel
**Ziel:** Entwicklung neuer/verbesserter Produkte, Verfahren oder Dienstleistungen
**Typ:** Boolean
**Erforderlich:** Ja

**Prompt:**
```
Prüfe, ob das Projektziel die Entwicklung von neuen ODER wesentlich verbesserten 
Produkten, Verfahren oder Dienstleistungen ist.

Es muss mindestens einer dieser Aspekte erfüllt sein:
- Neue Produkte
- Wesentlich verbesserte Produkte
- Neue Verfahren
- Wesentlich verbesserte Verfahren
- Neue Dienstleistungen
- Wesentlich verbesserte Dienstleistungen

Antworte im Format:
{
    "erfuellt": true/false,
    "kategorie": "Produkt/Verfahren/Dienstleistung",
    "neu_oder_verbessert": "neu/verbessert",
    "beschreibung": "...",
    "begruendung": "...",
    "quelle": "Dokument + Seite"
}
```

### Kriterium 5: Finanzierung
**Ziel:** Gesamtfinanzierung gesichert, Projektvolumen 10.000 - 100.000 EUR
**Typ:** Numerisch
**Erforderlich:** Ja

**Prompt:**
```
Prüfe die Finanzierung des Projekts.

Kriterien:
- Gesamtfinanzierung muss gesichert sein
- Projektvolumen zwischen 10.000 EUR und 100.000 EUR

Suche nach:
- Gesamtkosten/Projektvolumen
- Eigenmittel
- Beantragte Fördersumme
- Finanzierungsplan

Antworte im Format:
{
    "erfuellt": true/false,
    "gesamtkosten": number,
    "eigenmittel": number,
    "beantragte_foerderung": number,
    "finanzierung_gesichert": true/false,
    "in_range": true/false,
    "begruendung": "...",
    "quelle": "Dokument + Seite"
}
```

### Kriterium 6: Erfolgsaussicht
**Ziel:** Projekt ohne öffentliche Mittel nicht/nur verzögert realisierbar
**Typ:** Boolean
**Erforderlich:** Ja

**Prompt:**
```
Prüfe, ob das Projekt ohne öffentliche Förderung nicht oder nur verzögert 
realisierbar wäre.

Suche nach:
- Begründung zur Notwendigkeit der Förderung
- Wirtschaftliche Lage des Unternehmens
- Alternative Finanzierungsmöglichkeiten
- Zeitliche Verzögerung ohne Förderung

Antworte im Format:
{
    "erfuellt": true/false,
    "ohne_foerderung": "nicht_realisierbar/verzögert/realisierbar",
    "begruendung": "...",
    "quelle": "Dokument + Seite"
}
```

## Prüfmechanismus (Option 1 - Super-Lite)

### Ablauf (Vereinfacht & Robust)

**Schritt 1: Dokumente indexieren**
```
1. Beide PDFs hochgeladen (Projektskizze + Projektantrag)
2. PyMuPDF extrahiert Text
3. Simple Chunking (1000 Zeichen, 200 Overlap)
4. sentence-transformers erstellt Embeddings
5. ChromaDB speichert Vektoren
```

**Schritt 2: Kriterien sequenziell prüfen**
```python
# Pseudo-Code (Konzept für Option 1)

for kriterium in kriterienkatalog:
    # 1. RAG: Relevante Chunks holen
    chunks = chromadb.query(kriterium.search_query, top_k=5)
    
    # 2. Context zusammenstellen
    context = "\n\n".join(chunks)
    
    # 3. Prompt mit Context an LM Studio
    prompt = f"""
    Kontext aus Dokumenten:
    {context}
    
    Aufgabe:
    {kriterium.prompt}
    
    Antworte NUR mit JSON im Format:
    {kriterium.json_schema}
    """
    
    # 4. LLM abfragen
    result = lm_studio_client.query(prompt)
    
    # 5. JSON parsen & validieren
    parsed = json.loads(result)
    
    # 6. Speichern
    results.append(parsed)
    
    # 7. Status update für UI (alle 2 Sek via st.rerun)
    update_progress(f"Kriterium {i+1}/6 geprüft")
```

**Schritt 3: Ergebnisse speichern**
```
/data/projects/{projekt_id}/results/
  criteria_check_2025-11-13_14-30.json
```

### Workflow-Details (Robust & Einfach)

**Status-Tracking für UI:**
```python
# In session_state speichern
st.session_state.processing_status = {
    "step": "criteria_check",
    "current_criterion": 2,
    "total_criteria": 6,
    "progress_percent": 33,
    "last_update": "2025-11-13 14:30:15"
}

# UI liest alle 2 Sekunden neu aus
if st.session_state.get('auto_refresh', False):
    time.sleep(2)
    st.rerun()
```

**Error Handling:**
```python
# Einfach & robust
try:
    result = check_criterion(kriterium)
except LLMError as e:
    # Retry 1x
    result = check_criterion(kriterium)
except Exception as e:
    # Als "unklar" markieren, weitermachen
    result = {"erfuellt": None, "error": str(e)}
```

### Ergebnisformat
```json
{
    "projekt_id": "proj_2025_abc123",
    "pruefung_timestamp": "2025-11-08T10:00:00Z",
    "kriterien": [
        {
            "kriterium_id": "K001",
            "name": "Projektort",
            "erfuellt": true,
            "wert": "Hamburg",
            "begruendung": "Handelsregister bestätigt...",
            "quellen": ["projektantrag.pdf, Seite 2"],
            "confidence": 0.95
        }
    ],
    "zusammenfassung": {
        "gesamt": 6,
        "erfuellt": 6,
        "nicht_erfuellt": 0,
        "prozent": 100.0
    }
}
```

## Validierung

### Regeln
- Vollständigkeit aller 6 Kriterien
- Plausibilität der Werte
- Konsistenz zwischen Kriterien

### Nachprüfung
- Bei Unsicherheit (confidence < 0.7): Manuelle Prüfoption
- Dokumentenverweise anzeigen
- Änderungshistorie führen

## Reports

### Formate
- Einzelprüfung
- Gesamtübersicht
- Prüfprotokoll

### Export
- Markdown
- PDF
- JSON