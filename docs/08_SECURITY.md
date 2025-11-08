# Security
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 8. November 2025

## Übersicht

Sicherheitskonzept für die Antragsprüfung.

## Datenschutz

### Grundsätze
- Lokale Verarbeitung
- Keine Cloud-Dienste
- Verschlüsselte Speicherung

### Datensicherheit
- Verschlüsselung (AES-256)
- Sichere Löschung
- Zugriffsprotokollierung

## Zugriffskontrolle

### Benutzerrollen
- Administrator
- Prüfer
- Antragsteller

### Authentifizierung
- Lokale Accounts
- 2-Faktor optional
- Session-Management

## Dokumentensicherheit

### Upload
- Virus-Scanning
- Typ-Validierung
- Größenlimits

### Speicherung
- Verschlüsselt
- Versioniert
- Backup

## Audit-Logging

### Events
- Zugriffe
- Änderungen
- Prüfungen

### Format
```json
{
    "timestamp": "2025-11-08T10:00:00Z",
    "user": "pruefer_1",
    "action": "document_access",
    "resource": "projekt_123/doc_456",
    "result": "success"
}
```

## Compliance

### Datenschutz
- DSGVO-konform
- Löschkonzept
- Auskunftsrecht

### Protokollierung
- Prüfhistorie
- Änderungsverfolgung
- Exportfunktion