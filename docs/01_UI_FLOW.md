# UI Flow
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 8. November 2025

## Übersicht

Die Benutzeroberfläche führt den Antragsteller durch den Prozess der Antragseinreichung und -prüfung.

## Prozessschritte

### 1. Projekt anlegen
- Projektname
- Antragsteller/Firma
- Fördernummer (optional)
- Fördermodul (Dropdown)
- Projektart (Dropdown)

### 2. Dokumente hochladen
- Unterstützte Formate: PDF, DOCX, XLSX, TXT, MD
- Drag & Drop Upload
- Dokumentenbeschreibungen
- Validierung

### 3. Automatische Prüfung
- Live-Status pro Dokument
- Fortschrittsanzeige
- Manuelle Nachprüfung wenn nötig

### 4. Ergebnisübersicht
- Prüfungsergebnisse
- Exportmöglichkeiten
- Projektabschluss

## Technische Umsetzung

### Framework
- Streamlit als Basis
- Responsive Design
- Modular aufgebaut

### Seitenstruktur
1. Projektübersicht (project_overview.py)
2. Projektanlage (project_create.py)
3. Dokumenten-Upload (document_upload.py)
4. Prüfung (validation.py)
5. Ergebnisse (results.py)

## Design

### Farben
- Primary: #007BFF
- Success: #28A745
- Warning: #FFC107
- Danger: #DC3545

### Layout
- Klare Prozessschritte
- Fortschrittsanzeige
- Responsive für alle Geräte