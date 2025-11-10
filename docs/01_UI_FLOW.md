# UI Flow
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 8. November 2025

## Übersicht

Die Benutzeroberfläche führt den Antragsteller durch den Prozess der Antragseinreichung und -prüfung.

## Prozessschritte

### 1. Projekt anlegen
- Projekt-ID (automatisch generiert)
- Projektname
- Antragsteller/Firma
- Fördernummer (optional)
- Fördermodul (Dropdown)
- Projektart (Dropdown)

**Backend:** Pro Projekt wird ein eigener Ordner angelegt:
```
/data/projects/{projekt_id}/
  /uploads/
  /extracted/
  /results/
  metadata.json
```

### 2. Dokumente hochladen

Es werden genau **zwei Dokumente** hochgeladen:

#### Dokument 1: Projektskizze
**Beschreibung:** 2-3 seitige Projektbeschreibung mit folgenden Inhalten:
- Alle Ansprechpartner
- Unternehmensbeschreibung
- Technologischer Lösungsansatz
- Marktpotenzial und Vermarktung
- Gesamter Projektumfang

**Unterstützte Formate:** PDF, Word (DOCX), Textdatei

#### Dokument 2: Projektantrag (vorgefertigtes Formular)
**Beschreibung:** Ausgefülltes Antragsformular mit:
- Projektbeschreibung
- Projektkalkulation
- KMU-Erklärung
- Jahresabschluss
- Handelsregisterauszug
- Finanz- und Arbeitsplatzübersicht
- Lebensläufe (optional)

**Unterstützte Formate:** Definiert in Parser-Konfiguration

### 3. Automatische Prüfung
- RAG-Basis wird aufgebaut
- LLM-Integration wird aktiviert
- Kriterien werden sukzessive nach Kriterienkatalog geprüft
- Live-Status pro Kriterium
- Fortschrittsanzeige
- Manuelle Nachprüfung wenn nötig

### 4. Ergebnisübersicht
- Anzahl erfüllter Kriterien
- Anzahl nicht erfüllter Kriterien
- Detaillierte Prüfergebnisse
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