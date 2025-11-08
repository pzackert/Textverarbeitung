# Data Management
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 8. November 2025

## Übersicht

System zur Verwaltung von Projektdaten und Dokumenten.

## Projektstruktur

### Basis
```
/data
  /projects
    /{projekt_id}
      /uploads    # Original-Dokumente
      /extracted  # Extrahierte Daten
      /results    # Prüfergebnisse
      metadata.json
```

### Metadaten
```json
{
    "projekt_id": "proj_2025_abc123",
    "name": "Beispielprojekt",
    "created_at": "2025-11-08T10:00:00Z",
    "status": "in_progress",
    "documents": [],
    "results": []
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