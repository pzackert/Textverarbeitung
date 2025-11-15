# UI Flow
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 2.0  
**Stand:** 10. November 2025

## Übersicht

Die Benutzeroberfläche basiert auf **Streamlit** und führt den Benutzer durch einen klar strukturierten Prozess. Die UI ist minimalistisch, übersichtlich und Desktop-optimiert (mit Responsive-Design für Mobile).

## UI-Konfiguration

Zentrale Konfigurationsdatei für Streamlit-Settings:

```json
{
  "ui": {
    "theme": {
      "primaryColor": "#007BFF",
      "backgroundColor": "#FFFFFF",
      "secondaryBackgroundColor": "#F0F2F6",
      "textColor": "#262730",
      "font": "sans serif"
    },
    "layout": "wide",
    "sidebar": {
      "state": "expanded",
      "logo": "/assets/logo.png"
    }
  }
}
```

## Seitenstruktur & Flow

### Seite 0: Projektübersicht (Startseite)
**Datei:** `pages/00_project_overview.py`

#### Layout
```
┌─────────────────────────────────────────────────────┐
│  [Logo]    IFB PROFI - Antragsprüfung              │
│           Hamburger Förderung                        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Dieses Programm dient zur automatisierten Prüfung │
│  von Förderanträgen für das IFB PROFI Programm.    │
│                                                      │
├─────────────────────────────────────────────────────┤
│                                                      │
│  [➕ Neues Projekt anlegen]                         │
│                                                      │
├─────────────────────────────────────────────────────┤
│  Bestehende Projekte:                               │
│  ┌───────────────────────────────────────────────┐ │
│  │ ID    │ Name        │ Status    │ Aktion    │ │
│  ├───────────────────────────────────────────────┤ │
│  │ P001  │ Projekt A   │ ✓ Fertig  │ [Öffnen]  │ │
│  │ P002  │ Projekt B   │ ⏳ Läuft  │ [Öffnen]  │ │
│  │ P003  │ Projekt C   │ 📄 Neu    │ [Öffnen]  │ │
│  └───────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────┘
```

#### Funktionen
- Anzeige aller angelegten Projekte (tabellarisch)
- Status-Anzeige pro Projekt
- Öffnen bestehender Projekte zur Bearbeitung
- Button "Neues Projekt anlegen"

### Seite 1: Projekt anlegen
**Datei:** `pages/01_project_create.py`

#### Eingabefelder
- **Projekt-ID** (automatisch generiert, angezeigt)
- **Projektname** (Pflicht)
- **Antragsteller/Firma** (Pflicht)
- **Fördernummer** (optional)
- **Fördermodul** (Dropdown)
- **Projektart** (Dropdown)

#### Backend-Aktion
Nach dem Speichern wird automatisch erstellt:
```
/data/projects/{projekt_id}/
  /uploads/
  /extracted/
  /results/
  metadata.json
```

**Hinweis:** Backend-Struktur ist in `06_DATA_MANAGEMENT.md` dokumentiert.

### Seite 2: Dokumente hochladen
**Datei:** `pages/02_document_upload.py`

#### UI-Komponenten

**Best Practice Streamlit:**
- Nutze neueste Streamlit-Komponenten
- Drag & Drop Upload (st.file_uploader mit drag_and_drop=True)
- Progress-Bars für Upload
- Real-time Feedback

#### Upload-Bereiche

**Dokument 1: Projektskizze**
```
┌─────────────────────────────────────────────┐
│ 📝 Projektskizze (2-3 Seiten)              │
├─────────────────────────────────────────────┤
│ • Ansprechpartner                           │
│ • Unternehmensbeschreibung                  │
│ • Technologischer Lösungsansatz             │
│ • Marktpotenzial und Vermarktung            │
│ • Projektumfang                             │
├─────────────────────────────────────────────┤
│ [Drag & Drop oder Durchsuchen]             │
│                                             │
│ Upload: [████████░░] 80% (2.4 MB / 3 MB)  │
│ ✓ projektskizze.pdf hochgeladen             │
└─────────────────────────────────────────────┘
```

**Dokument 2: Projektantrag**
```
┌─────────────────────────────────────────────┐
│ 📋 Projektantrag (Formular)                │
├─────────────────────────────────────────────┤
│ • Projektbeschreibung                       │
│ • Projektkalkulation                        │
│ • KMU-Erklärung                            │
│ • Jahresabschluss                          │
│ • Handelsregisterauszug                     │
│ • Finanz- und Arbeitsplatzübersicht        │
│ • Lebensläufe (optional)                   │
├─────────────────────────────────────────────┤
│ [Drag & Drop oder Durchsuchen]             │
│                                             │
│ ✓ projektantrag.pdf hochgeladen             │
└─────────────────────────────────────────────┘
```

**Zusätzliche Dokumente**
```
┌─────────────────────────────────────────────┐
│ 📎 Weitere Dokumente (optional)            │
├─────────────────────────────────────────────┤
│ ✓ lebenslauf_ceo.pdf                       │
│ ✓ marktanalyse.docx                        │
│ [+ Weiteres Dokument hinzufügen]           │
└─────────────────────────────────────────────┘
```

**Hinweis:** Unterstützte Formate werden aus Parser-Konfiguration geladen.

#### Upload-Prozess
1. Dateiauswahl (Drag & Drop oder Browse)
2. Validierung (Format, Größe)
3. Upload mit Progress Bar
4. Bestätigung ✓
5. Backend-Speicherung in `/uploads/`

### Seite 3: Automatische Prüfung
**Datei:** `pages/03_validation.py`

#### Oberer Bereich: Prozess-Status (Vereinfacht für MVP)

```
┌─────────────────────────────────────────────────────┐
│  Verarbeitungsstatus                                │
├─────────────────────────────────────────────────────┤
│  Schritt 1/4: Dokumente parsen... ✓                │
│  Schritt 2/4: RAG indexieren... (50%)              │
│  Schritt 3/4: LLM vorbereiten... ⏳                │
│  Schritt 4/4: Kriterien prüfen... ⏹                │
│                                                      │
│  [██████░░░░] 50% - Bitte warten...                │
└─────────────────────────────────────────────────────┘
```

**Implementation:** 
- `st.progress()` für Balken
- `st.text()` für Status-Updates
- Update alle 2 Sek via `st.rerun()` + Session State

#### Unterer Bereich: Kriterienliste

```
┌─────────────────────────────────────────────────────────┐
│  Förderkriterien                                        │
├────┬─────────────────────┬──────────┬─────────┬────────┤
│ #  │ Kriterium           │ Status   │ Ergebnis│ Aktion │
├────┼─────────────────────┼──────────┼─────────┼────────┤
│ 1  │ Projektort          │ ⏳ Prüft │ -       │        │
│ 2  │ Unternehmensalter   │ ⏹ Warte │ -       │        │
│ 3  │ Projektbeginn       │ ⏹ Warte │ -       │        │
│ 4  │ Projektziel         │ ⏹ Warte │ -       │        │
│ 5  │ Finanzierung        │ ⏹ Warte │ -       │        │
│ 6  │ Erfolgsaussicht     │ ⏹ Warte │ -       │        │
└────┴─────────────────────┴──────────┴─────────┴────────┘
```

Nach Prüfung:
```
├────┬─────────────────────┬──────────┬─────────┬────────┤
│ 1  │ Projektort          │ ✓ OK     │ Hamburg │ [📄]   │
│ 2  │ Unternehmensalter   │ ✓ OK     │ 5 Jahre │ [📄]   │
│ 3  │ Projektbeginn       │ ⚠️ Unklar│ ?       │ [✏️]   │
```

**[✏️] = Manuelle Korrektur (Vereinfacht für MVP)**
- **Input-Feld** erscheint direkt in der Tabelle
- Benutzer kann Wert überschreiben
- Kommentarfeld für Begründung
- Dokument separat downloadbar für eigene Prüfung

#### Live-Updates (Streamlit Rerun-Strategie)
- Status-Updates alle 2 Sekunden via `st.rerun()`
- Text-basierte Fortschrittsanzeige: "Schritt 2/4: RAG wird aufgebaut..."
- Prozentsatz-Anzeige: "Progress: 50%"
- **Robust:** Kein Threading, keine Websockets - nur einfaches Polling

### Seite 4: Ergebnisübersicht
**Datei:** `pages/04_results.py`

#### Zusammenfassung
```
┌─────────────────────────────────────────────┐
│  Prüfungsergebnis                           │
├─────────────────────────────────────────────┤
│  ✓ 6/6 Kriterien erfüllt (100%)            │
│  ⏱ Prüfung durchgeführt: 10.11.2025 14:30 │
└─────────────────────────────────────────────┘
```

#### Detaillierte Kriterien
```
┌─────────────────────────────────────────────┐
│  1. Projektort: ✓ Erfüllt                  │
│     → Hamburg                               │
│     Quelle: projektantrag.pdf, Seite 2      │
├─────────────────────────────────────────────┤
│  2. Unternehmensalter: ✓ Erfüllt           │
│     → Gegründet 2020 (5 Jahre)             │
│     Quelle: handelsregister.pdf, Seite 1    │
└─────────────────────────────────────────────┘
```

#### Export-Funktionen
- [📥 Ergebnis als JSON exportieren] **(MVP - einfach!)**
- [📥 Dokumente als ZIP herunterladen] **(MVP - einfach!)**
- [� Protokoll als Markdown] **(MVP - einfach!)**

**Hinweis:** PDF-Export kommt in v2 (reportlab-Dependency vermeiden im MVP)

#### Projektabschluss
- [✓ Projekt abschließen]
- [← Zurück zur Übersicht]

## Technische Umsetzung

### Framework
- **Streamlit** (neueste stabile Version)
- Responsive Design (Desktop-First, Mobile-fähig)
- Modular aufgebaut
- Best Practices beachten

### Streamlit-Komponenten (Option 1 - Super-Lite MVP)

**Verwendete Streamlit-Features:**
- ✅ `st.file_uploader()` - Drag & Drop (built-in, einfach!)
- ✅ `st.text_input()`, `st.selectbox()` - Formulare
- ✅ `st.dataframe()` oder `st.table()` - Tabellen
- ✅ `st.progress()` + `st.text()` - Progress-Anzeige
- ✅ `st.download_button()` - JSON/ZIP-Download
- ✅ `st.rerun()` - Automatisches Refresh alle 2 Sek
- ✅ `st.session_state` - Zustandsverwaltung
- ✅ `st.spinner()` - Einfache Loading-Indikator

**NICHT verwendet (zu komplex für MVP):**
- ❌ Custom Components
- ❌ Modals/Overlays (Streamlit hat keine nativen!)
- ❌ PDF-Generierung (kommt v2)
- ❌ Websockets/Async
- ❌ Komplexe Visualisierungen

### Seitenstruktur
```
frontend/
  pages/
    00_project_overview.py    # Projektübersicht (Startseite)
    01_project_create.py      # Projekt anlegen
    02_document_upload.py     # Dokumenten-Upload
    03_validation.py          # Automatische Prüfung
    04_results.py             # Ergebnisübersicht
  config/
    ui_config.json           # UI-Konfiguration
  assets/
    logo.png                 # Logo
```

## Design-Prinzipien

### Farben (aus UI-Config)
- **Primary:** #007BFF (Hauptfarbe für Buttons, Links)
- **Success:** #28A745 (Erfolgreiche Aktionen)
- **Warning:** #FFC107 (Warnungen, unsichere Prüfungen)
- **Danger:** #DC3545 (Fehler, nicht erfüllt)
- **Info:** #17A2B8 (Informationen)

### Layout
- **Minimalistisch** - Nur notwendige Elemente
- **Übersichtlich** - Klare Hierarchie
- **Konsequent** - Einheitliche Patterns
- **Responsive** - Desktop & Mobile

### Typography
- **Hauptschrift:** Sans Serif (aus Streamlit Config)
- **Überschriften:** Klar und prominent
- **Body:** Lesbar, ausreichend Größe

## Besondere Anforderungen

### Upload-Funktionalität
- **Drag & Drop** obligatorisch
- **Progress-Bars** für alle Uploads > 1 MB
- **Real-time Feedback** während Upload
- **Validierung** vor Upload (Format, Größe)

### Prozess-Transparenz
- **Live-Status** während Verarbeitung
- **Fortschrittsanzeigen** für lange Prozesse
- **Klar ersichtlich** was im Hintergrund passiert

### Manuelle Nachprüfung
- **Modal/Overlay** zum Dokumenten-Review
- **Kontextanzeige** (relevante Dokumentenstelle)
- **Eingabefeld** für manuellen Wert
- **Kommentarfeld** für Begründung

### Export-Funktionen
- **PDF-Export** für Berichte
- **JSON-Export** für Daten
- **Protokoll-Export** für Nachvollziehbarkeit