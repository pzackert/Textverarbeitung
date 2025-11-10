# Criteria Engine
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 8. November 2025

## Übersicht

System zur Definition und Prüfung von Förderkriterien. Insgesamt werden **6 Kriterien** geprüft.

## Kriterienkatalog

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

## Prüfmechanismus

### Ablauf
1. Beide Dokumente (Projektskizze + Projektantrag) werden indexiert
2. RAG-Basis wird aufgebaut (ChromaDB)
3. Kriterien werden **sukzessive** geprüft (eines nach dem anderen)
4. Pro Kriterium:
   - Relevanter Kontext wird aus RAG abgerufen
   - Prompt mit Kontext wird an LLM gesendet
   - LLM gibt strukturierte Antwort zurück
   - Ergebnis wird validiert und gespeichert
5. Alle Ergebnisse werden aggregiert

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