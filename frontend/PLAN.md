# Frontend Rebuild Plan (Streamlit MVP)

> Ziel: Umsetzung des aktualisierten "Optimiertes Frontend-Konzept" als stabile, getestete Streamlit-App im Verzeichnis `frontend/`.

## 1. Struktur & Setup

1. **Grundgerüst anlegen**
   - `frontend/app.py` als Single-Entry mit `st.set_page_config` und Layout-Shell.
   - Unterordner: `components/`, `services/`, `state/`, `styles/`, `assets/`.
   - `styles/custom.css` nur für unterstützte Anpassungen (Spacing, Cards, Farbverläufe).
2. **Utility-Module**
   - `state/session_keys.py`: zentrale Session-State-Schlüssel & Defaults.
   - `theme/tokens.py`: Farb- und Typografie-Token basierend auf Streamlit-Theme.
   - `analytics/service.py`: Aggregationen (z. B. Heatmap-Daten) mit Mock-Fallback für ≤50 Projekte.
3. **Demo-Daten absichern**
   - `project_service.ensure_demo_project()` beim Start, Logging im Terminal.

## 2. Seitenaufbau (Command Center als SPA)

1. **Header** mit Logo, Titel, Settings-Popover (LLM/Kriterien/Theme) → real-time Feedback + Validierung.
2. **Sidebar** (Projektnavigator) + Filter (bis 50 Projekte performant).
3. **Main Command Center**
   - Quick-Action-Karten (Neu, Fortsetzen, Dashboard Link Stub).
   - "So funktioniert's"-Stepper (Tabs) mit GIF/Placeholder.
   - Statistik-Karten ohne externe Data-Contracts (nur Session/Projekt-basiert).
   - GitHub-Style Kalender (Streamlit Nivo) für letzte 12 Monate, nur interne Counts.
4. **Detail Rail / Kontextbereich** für Vermerke & Dokumentinfos bei aktiven Projekten.

## 3. Prozess-Abschnitte

1. **Upload-Bereich**
   - Drag-and-drop Zone, Dateipreview, Auto-Tagging (Namensheuristiken).
   - Upload-Formen, Integration `handle_document_upload` + Status-Feedback.
2. **Live-Prüfung**
   - dreispaltiges Layout (Progress + Kriterien, Terminal, KI-Chat Stub).
   - Session-State-Management für Logs, Fortschritt, Chat-Historie.
3. **Ergebnis-Tabs**
   - Übersicht, KI-Zusammenfassung, Visualisierungen (Plotly placeholders), Vermerke.
   - Download- & Folgeaktionen (PDF stub, E-Mail stub, Archiv). 

## 4. Komponentenliste

- `components/header.py`
- `components/sidebar.py`
- `components/command_center.py`
- `components/upload_panel.py`
- `components/review_dashboard.py`
- `components/results_view.py`
- `components/heatmap.py` (wrap für `streamlit_nivo`)
- `components/toast.py` (optionale Hinweise)

## 5. Testing & Qualitätssicherung

1. **Unit Tests (pytest)**
   - `analytics/service.py` (Zeiträume, Aggregation ≤50 Projekte).
   - `state/session_keys.py` Defaults.
2. **Streamlit Manual QA**
   - Szenario 1: Neues Projekt anlegen → Upload → Kriterienlauf → Ergebnis.
   - Szenario 2: Demo-Projekt laden → Heatmap rendern → Vermerk speichern.
   - Szenario 3: Wiederholtes Laden (Session-Reset) zur Sicherstellung stabiler Defaults.
3. **Visual QA**
   - Light & Dark Theme Check (per Streamlit Setting).
   - Fokus/Keyboard-Navigation auf Buttons, Tabs, Upload.
   - Layout in 1280px Breite und schmalem Fenster (~900px) prüfen.
4. **Performance**
   - Log-Länge begrenzen (z. B. 200 Einträge) zur Session-Stabilität.
   - Heatmap-Daten via `st.cache_data(ttl=3600)`.

## 6. Abschluss-Checkliste vor Handover

- [ ] Alle Komponenten in `frontend/` vorhanden, keine TODO-Reste.
- [ ] `uv run streamlit run frontend/app.py` zweimal ohne Fehler durchgelaufen.
- [ ] Pytest Suite (`uv run pytest frontend tests/frontend`) grün.
- [ ] README-Abschnitt (Frontendlauf) aktualisiert.
- [ ] Screenshots/Notizen der QA in `docs/frontend-validation.md`.
- [ ] Offene Fragen/Follow-ups dokumentiert für gemeinsames Testing.
