# Data Management
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 2.0 (Option 1 MVP + Enterprise Features)  
**Stand:** 8. November 2025

## Übersicht

System zur Verwaltung von Projektdaten und Dokumenten.

## Projektstruktur - ✅ OPTION 1

### Basis - ✅ OPTION 1
**Für jedes Projekt wird ein eigener Ordner angelegt:**

```
/data
  /projects
    /{projekt_id}           # z.B. proj_2025_abc123
      /uploads              # Original-Dokumente
        projektskizze.pdf
        projektantrag.pdf
      /extracted            # Extrahierte Daten (JSON)
        projektskizze.json
        projektantrag.json
      /results              # Prüfergebnisse
        criteria_check_20251108.json
      metadata.json
```

### Metadaten - ✅ OPTION 1 (Einfache Version)
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

---

## Dateimanagement

### ✅ OPTION 1 (Basis-Features):

- **Upload:** Einfacher File-Upload über Streamlit
- **Speicherung:** Lokales Filesystem ohne Encryption
- **Format-Check:** Nur PDF/DOCX/XLSX Prüfung

---

### ⚠️ OPTION 2+ (Erweiterte Features):

#### Upload
- Virenprüfung (ClamAV Integration)
- Erweiterte Formaterkennung
- Deduplizierung (Hash-Check)
- Versionierung (Git-basiert)

#### Speicherung
- Verschlüsselte Speicherung
- S3-kompatible Object Storage
- Backup-Integration

#### Archivierung
- Automatische Komprimierung
- Retention Policy
- Cleanup-Jobs

---

## Metadaten-Handling

### ✅ OPTION 1 (Einfaches Tracking):

**Tracking:** Einfache JSON-Files pro Projekt

**Indizierung:** Keine Volltextsuche in MVP, nur Projekt-Liste

---

### ⚠️ OPTION 2+ (Erweitert):

#### Tracking
- Dokumentenhistorie mit Audit-Trail
- Bearbeitungsstatus-Workflow
- Detailed Logging

#### Indizierung
- Volltextsuche (Elasticsearch)
- Metadaten-Suche
- Cross-Projekt-Verknüpfungen

---

## Backup - ⚠️ OPTION 2+ ONLY

**In Option 1: Keine automatischen Backups**

### OPTION 2+ Strategie:
- Inkrementell täglich
- Voll wöchentlich
- Verschlüsselt

### Recovery:
- Point-in-Time
- Selektiv
- Verifizierung