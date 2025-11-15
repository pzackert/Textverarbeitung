# UI Redesign Plan (IFB PROFI)
**Stand:** 14. November 2025

## Ziele
- Vereinheitlichte UX zwischen Projektübersicht, Wizard-Flow und Ergebnisdarstellung
- Frontend-Komponenten greifen konsequent auf Backend-Services (`projekt_manager`, `dokument_manager`, Kriterien-Engine) zu
- Stärker geführter Prozess mit permanent sichtbarer Fortschrittsanzeige
- Konsistentes Corporate-Design (Dunkelblau/Weiß/Rot/Hellgrün + viel Weißraum) nach Vorgabe
- Testbares Demo-Projekt inklusive vordefinierter Dokumente & Stati

## Informationsarchitektur
1. **Sidebar (global)**
   - Projektliste mit Status-Badges (Icon + Text)
   - Schneller Zugriff auf zuletzt bearbeitete Projekte
   - Kompakte KPIs (z. B. Anzahl Projekte je Status)
2. **Overview Screen (Main)**
   - Hero-Intro mit Call-to-Action „Neues Projekt anlegen“
   - Tabellarische Übersicht aller Projekte (Status, letzter Schritt, Ergebnis)
   - Schnellfilter + Suchfeld
   - Cards für zuletzt bearbeitete Projekte
3. **Project Wizard**
   - Persistenter Fortschrittsbalken (4 Schritte: Metadaten → Upload → Prüfung → Ergebnisse)
   - Jede Sektion lädt Daten über Backend-Service & Session State
   - CTA-Reihe unten (Zurück/Weiter, Aktionen je Schritt)

## Wizard-Schritte & Backend-Verknüpfung
| Schritt | UI-Fokus | Backend-Aufruf |
| --- | --- | --- |
| 1. Metadaten | Formular (Name, Antragsteller, Modul, Art, Beschreibung) | `backend.projekt_manager.create_projekt` + `update_projekt_metadata` |
| 2. Upload | Kachel je Dokumenttyp (aus `config/criteria_catalog.json`) mit Beschreibung & benötigten Kriterien, Upload + Status | `backend.dokument_manager.save_document` |
| 3. Prüfung | Statusfeed (Parsing → Chunking → Kriterien) + Kriterienliste mit Live-Status | `backend.parsers.parser.parse_document`, `backend.rag.chunker`, `backend.core.criteria.check_all_criteria` |
| 4. Ergebnisse | Zusammenfassung, Kriterien-Accordion, Export-Buttons | Lesezugriff `results.json` + Report-Helper |

## Dokumentanforderungen im Upload-Step
- Dynamisch aus `criteria_catalog.json`
- Zeige pro Dokument: Name, Beschreibung, benötigte Kriterien, unterstützte Formate, Hinweis auf Kriterienkatalog
- Optionaler Link zu PDF/Markdown-Dokumentation
- Upload-Komponente merkt sich Dateityp, ruft `save_document(projekt_id, doc_type, file)`

## Design Tokens & CSS
- Primärfarbe `#0D2F66`, Sekundär-Akzente `#D7263D` (Rot) & `#4CAF50` (Hellgrün)
- Großzügiger Weißraum, 16/24px Spacing-System
- Typografie: `"Inter", "DM Sans", sans-serif` (Fallback: Streamlit Default)
- Utility-Klassen für Cards, Status-Pills, Progress Steps (CSS in `frontend/styles/copalette.css`)

## Test-/Demo-Projekt
- Seeder erstellt unter `data/projects/demo_projekt` inkl. `metadata.json`, Dummy-Dokumente & Ergebnisse
- Wird automatisch angelegt, falls nicht vorhanden, beim Start der App (`ensure_demo_project()`)
- Ermöglicht sofortige Demo des Wizard-Flows ohne Upload

## Deployment-Notizen
- Streamlit bleibt Framework; Layout via `st.container` + `st.columns` + Custom CSS
- Alle Dateipfade relativ zur Repo-Root (`Path(__file__).resolve().parents[1]`)
- Neue Helpers:
  - `frontend/services/project_service.py`
  - `frontend/services/wizard_state.py`
  - `frontend/components/progress_tracker.py`
  - `frontend/styles/copalette.css`

## Offene Punkte
- Erweiterung PDF/JSON-Export (später)
- Echtzeit-Status-Updates bei langen Prüfungen (Polling, future work)
- Optional: API-Schicht für Frontend (FastAPI)
