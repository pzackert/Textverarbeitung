# Criteria Engine
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 8. November 2025

## Übersicht

System zur Definition und Prüfung von Förderkriterien.

## Kriterienkatalog

### Struktur
```json
{
    "kriterium_id": "K001",
    "name": "Betriebsstätte Hamburg",
    "beschreibung": "Prüfung des Unternehmensstandorts",
    "typ": "boolean",
    "erforderlich": true,
    "prueflogik": {
        "prompt_template": "...",
        "extraktion_regeln": [],
        "validierung": []
    }
}
```

### Kriterientypen
1. Boolean (ja/nein)
2. Numerisch (Werte/Ranges)
3. Kategorie (Auswahl)
4. Text (Freitext)

## Prüfmechanismus

### Ablauf
1. Kriterium laden
2. Kontext sammeln
3. LLM-Prüfung
4. Ergebnis validieren

### Ergebnisformat
```json
{
    "kriterium_id": "K001",
    "erfuellt": true,
    "wert": "Hamburg",
    "begruendung": "Handelsregister bestätigt...",
    "quellen": ["handelsregister.pdf"],
    "confidence": 0.95
}
```

## Validierung

### Regeln
- Vollständigkeit
- Plausibilität
- Konsistenz

### Nachprüfung
- Manuelle Prüfoption
- Dokumentenverweise
- Änderungshistorie

## Reports

### Formate
- Einzelprüfung
- Gesamtübersicht
- Prüfprotokoll

### Export
- Markdown
- PDF
- JSON