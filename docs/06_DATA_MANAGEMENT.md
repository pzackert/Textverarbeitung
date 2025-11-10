# Data Management
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 8. November 2025

## Übersicht

System zur Verwaltung von Projektdaten und Dokumenten.

## Projektstruktur

### Basis
**Für jedes Projekt wird ein eigener Ordner angelegt:**

```
/data
  /projects
    /{projekt_id}           # z.B. proj_2025_abc123
      /uploads              # Original-Dokumente
        projektskizze.pdf
        projektantrag.pdf
      /extracted            # Extrahierte Daten
        projektskizze.json
        projektantrag.json
      /results              # Prüfergebnisse
        criteria_check_20251108.json
      metadata.json
```

### Metadaten
```json
{
    "projekt_id": "proj_2025_abc123",
    "name": "Beispielprojekt",
    "created_at": "2025-11-08T10:00:00Z",
    "status": "in_progress",
    "documents": [
        {
            "id": "doc_001",
            "type": "projektskizze",
            "filename": "projektskizze.pdf",
            "uploaded_at": "2025-11-08T10:05:00Z"
        },
        {
            "id": "doc_002",
            "type": "projektantrag",
            "filename": "projektantrag.pdf",
            "uploaded_at": "2025-11-08T10:06:00Z"
        }
    ],
    "results": [
        {
            "type": "criteria_check",
            "timestamp": "2025-11-08T10:15:00Z",
            "file": "results/criteria_check_20251108.json"
        }
    ]
}
```

## Dateimanagement

### Upload
- Virenprüfung
- Formaterkennung
- Deduplizierung
- Versionierung

### Speicherung
- Lokales Filesystem
- Strukturierte Ablage
- Backup-Integration

### Archivierung
- Komprimierung
- Retention Policy
- Cleanup-Jobs

## Metadaten-Handling

### Tracking
- Dokumentenhistorie
- Bearbeitungsstatus
- Prüfergebnisse

### Indizierung
- Volltextsuche
- Metadaten-Suche
- Verknüpfungen

## Backup

### Strategie
- Inkrementell täglich
- Voll wöchentlich
- Verschlüsselt

### Recovery
- Point-in-Time
- Selektiv
- Verifizierung