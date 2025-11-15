# Security
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 2.0 (Option 1 MVP + Enterprise Features)  
**Stand:** 8. November 2025

## Übersicht

Sicherheitskonzept für die Antragsprüfung.

---

## Datenschutz

### ✅ OPTION 1 (Grundsätze - Basis):
- ✅ Lokale Verarbeitung (LM Studio + ChromaDB)
- ✅ Keine Cloud-Dienste
- ✅ Einfache lokale Speicherung (keine Encryption in MVP)

---

### ⚠️ OPTION 2+ (Erweiterte Datensicherheit):
- Verschlüsselte Speicherung (AES-256)
- Sichere Löschung (Overwrite)
- Zugriffsprotokollierung (Audit-Log)

---

## Zugriffskontrolle

### ✅ OPTION 1 (Single-User):
**Keine Benutzer-Authentifizierung in MVP**
- Lokale Desktop-Anwendung
- Kein Multi-User-Support
- Keine Sessions

---

### ⚠️ OPTION 2+ (Multi-User):

#### Benutzerrollen
- Administrator
- Prüfer
- Antragsteller

#### Authentifizierung
- Lokale Accounts
- 2-Faktor optional
- Session-Management

---

## Dokumentensicherheit

### ✅ OPTION 1 (Basis):

**Upload:**
- ✅ Typ-Validierung (PDF/DOCX/XLSX)
- ✅ Größenlimits (max. 50MB)
- ❌ Kein Virus-Scanning in MVP

**Speicherung:**
- ✅ Lokales Filesystem
- ❌ Keine Verschlüsselung in MVP
- ❌ Kein Backup-System in MVP

---

### ⚠️ OPTION 2+ (Erweitert):

#### Upload
- Virus-Scanning (ClamAV)
- Erweiterte Validierung
- Größenlimits

#### Speicherung
- Verschlüsselt (AES-256)
- Versioniert (Git-basiert)
- Automatisches Backup

---

## Audit-Logging - ⚠️ OPTION 2+ ONLY

**In Option 1: Kein Audit-Logging**

### OPTION 2+ Events:
- Zugriffe
- Änderungen
- Prüfungen

### Format:
```json
{
    "timestamp": "2025-11-08T10:00:00Z",
    "user": "pruefer_1",
    "action": "document_access",
    "resource": "projekt_123/doc_456",
    "result": "success"
}
```

---

## Compliance

### ✅ OPTION 1 (Basis):

**Datenschutz:**
- ✅ DSGVO-konform (lokale Verarbeitung, keine Cloud)
- ✅ Manuelle Löschung möglich (Ordner löschen)
- ❌ Kein automatisches Löschkonzept

---

### ⚠️ OPTION 2+ (Erweitert):

**Datenschutz:**
- DSGVO-konform
- Automatisches Löschkonzept
- Auskunftsrecht (API)

**Protokollierung:**
- Vollständige Prüfhistorie
- Änderungsverfolgung
- Export-Funktion