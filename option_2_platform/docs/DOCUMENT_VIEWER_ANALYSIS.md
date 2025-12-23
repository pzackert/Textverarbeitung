# Document-Viewer Analyse

## 1. IST-Zustand
- **Tech-Stack:** Vanilla JS + PDF.js (eingebunden via `pdfjsLib`), Mammoth.js für DOCX, SheetJS für XLSX, einfache `fetch`-Aufrufe, DOM-Manipulation. Keine React/SPA-Struktur.
- **Code-Struktur:**
  - Templates: [frontend/templates/partials/viewer_content.html](frontend/templates/partials/viewer_content.html) rendert Toolbar/Canvas, ruft `window.renderPDF` (existiert nicht) und setzt `currentDocId`.
  - Logik: [frontend/static/js/review.js](frontend/static/js/review.js) enthält State (`currentDocState`), Toggle-Logik, RAG-Calls, Render-Funktionen (`updateViewer`, `renderPdf`, `renderWord`, `renderExcel`, `renderText`), PDF.js Hilfen (`renderPage`, `queueRenderPage`) und Lifecycle (DOMContentLoaded).
  - Styles: [frontend/static/css/review-cockpit.css](frontend/static/css/review-cockpit.css) (nicht detailliert geprüft).
- **Dependencies & Versionen:** PDF.js worker wird hart auf `/static/js/libs/pdf.worker.min.js` gesetzt; Mammoth.js, SheetJS (XLSX) werden clientseitig genutzt; Versionen nicht zentral dokumentiert.
- **API-Endpoints (relevant für Viewer):**
  - `/api/projects/{id}/documents` → liefert Metadaten inkl. `has_annotated` (neu), wird beim Init geladen.
  - `/api/projects/{id}/documents/uploads/{filename}` → Original-Download/Anzeige (wird als iframe-src genutzt).
  - `/api/projects/{id}/documents/annotated/{filename}` → Annotate-Download/Anzeige (Dateiname wird geraten).
  - Keine dezidierten Endpoints für Seiten-Sprung oder Preview-Metadaten; PDF wird direkt als URL geladen.

## 2. Identifizierte Probleme
### Problem 1: PDF-Rendering-Pfad inkonsistent
- **Beschreibung:** Template ruft `window.renderPDF` und erwartet Canvas/Text-Layer; review.js nutzt hingegen iframe (`viewerFrame.src = url`) und hat eigene `renderPdf`/`renderPage` Logik, die nie aufgerufen wird.
- **Manifestation:** Toolbar (Seitenanzeige/Zoom) aus Template ist funktionslos, PDF.js Rendering passiert nicht, Navigation/Sprung unmöglich. Unterschiedliche Pfade (iframe vs Canvas) kollidieren.
- **Root-Cause:** Doppelte/inkonsistente Implementierung (Template vs review.js), fehlender Aufruf von `renderPdf`, verwaiste `renderPDF`-Referenz.
- **Betroffene Use Cases:** UC1, UC2, UC3, UC4, UC6 (Seiten-Sprung unmöglich).

### Problem 2: Annotated-Toggle rät Dateinamen
- **Beschreibung:** Annotated-Datei wird über Heuristik gebaut (`annotated_${fname}` oder `fname.replace(' .', '_annotated.')`), statt serverseitig gelieferter eindeutiger URL.
- **Manifestation:** Annotated-Toggle oft disabled oder lädt 404, besonders bei `_annotated` Suffix oder Non-PDF (docx/xlsx).
- **Root-Cause:** Kein API-Feld für `annotated_url`/`annotated_file` im Dokument-List-Response; Client spekuliert.
- **Betroffene Use Cases:** UC2, UC4, UC1 (wenn erstes Dokument Annotate benötigt).

### Problem 3: Kein Format-spezifisches Cleanup / Race Conditions
- **Beschreibung:** Beim Dokumentwechsel wird iframe src gewechselt, Canvas/Text-Layer bleiben; laufende PDF.js Tasks werden nicht abgebrochen; State wird partiell zurückgesetzt.
- **Manifestation:** Alter Content sichtbar, Memory-Leaks, teils „Kein Dokument ausgewählt“/leere Fläche nach Wechsel.
- **Root-Cause:** `updateViewer` setzt nur basic DOM, ruft nicht `cleanupPdf`, nicht `cancelRendering`, keine AbortController bei fetch (Word/Excel/Text).
- **Betroffene Use Cases:** UC2, UC4, UC1.

### Problem 4: Seiten-Sprung nicht implementiert
- **Beschreibung:** Chat-Quelle „Seite 8“ kann nicht im Viewer angewandt.
- **Manifestation:** Klick auf Quelle öffnet PDF, bleibt auf Seite 1.
- **Root-Cause:** Kein Parameter für Page im `renderDocument`, kein Hook auf Link-Klicks, PDF.js Pfad ungenutzt.
- **Betroffene Use Cases:** UC3, UC6.

### Problem 5: Initial Load fehlt First-Doc Render
- **Beschreibung:** DOMContentLoaded lädt nur annotated list, nicht das erste Dokument; `renderDocument` wird nicht automatisch ausgelöst.
- **Manifestation:** „Kein Dokument ausgewählt“/leerer Viewer beim Öffnen.
- **Root-Cause:** Kein Auto-Select/Auto-Open der ersten Sidebar-Datei; Sidebar-Klick-Handler nicht im Scope von review.js.
- **Betroffene Use Cases:** UC5.

### Problem 6: fehlende Format-spezifische Viewer
- **Beschreibung:** Alle Formate werden im selben Container behandelt, ohne UI/UX-spezifische Komponenten (Tabs für Sheets, Word layout, Text highlighting). XLSX rendert nur erste Sheet, keine Navigation; DOCX ohne Scroll/height mgmt.
- **Manifestation:** Excel-Sheets nicht wechselbar; Markdown ohne Syntax-Highlight; Word-Darstellung basic.
- **Root-Cause:** Minimal-Implementierung von SheetJS/Mammoth ohne UI und ohne State.
- **Betroffene Use Cases:** UC1, UC2 (Formatwechsel), UC4 (annotierte DOCX/XLSX).

### Problem 7: Fehlender Request-Blocking/Loading-State
- **Beschreibung:** Viewer lädt parallel RAG-Auto-Ingest; keine dedizierte Loading/Retry-UI pro Dokument.
- **Manifestation:** Nutzer-Klick während fetch kann race conditions triggern (altes fetch überschreibt neues Rendering). Kein AbortController.
- **Root-Cause:** Fehlendes Request-Lifecycle-Management.
- **Betroffene Use Cases:** UC1, UC2.

### Problem 8: API-Integration unpräzise
- **Beschreibung:** Viewer nutzt `/documents/uploads/{filename}` statt signierte URLs/`Content-Disposition`. Keine HEAD/metadata-Abfragen, keine Content-Type-Validierung.
- **Manifestation:** Caching/Content-Type Mismatch möglich; Annotated-Download je nach Format fehlschlagend.
- **Root-Cause:** API-Design minimalistisch, keine preflight Metadata.
- **Betroffene Use Cases:** UC1-UC4.

## 3. Robuste Lösung (Konzept)
### Architektur-Empfehlung
- **Single Viewer Shell** mit Format-spezifischen Renderern:
  - `DocumentViewer` orchestriert State: `documentId`, `filename`, `format`, `page`, `annotated`, `source`, `loading`, `error`, `versionId` (to cancel stale renders).
  - Renderer-Komponenten: `PdfViewer`, `DocxViewer`, `ExcelViewer`, `TextViewer`.
- **State-Management:** zentrale store (z. B. Redux/Zustand/Context) oder ein klarer JS-Modul-Store; jede Render-Request bekommt `requestId`; bei Wechsel alte Requests abgebrochen (AbortController) und RenderTasks (PDF.js) gecancelt.
- **Routing/Deep-Link:** Query params `?doc=foo.pdf&view=annotated&page=8`; Chat-Links setzen diese Params; Viewer liest Params und lädt zielgerichtet.
- **Cleanup:** Jeder Renderer stellt `dispose()` bereit (cancel render, remove event listeners, revoke ObjectURLs).

### Library-Empfehlungen
- **PDF:** Offizielles PDF.js (pdfjs-dist) mit `<canvas>` + textLayer; nutzt `PDFLinkService` oder eigene Scroll-to-page; Option: `pdfjsViewer.PDFViewer` für Paging/Zoom.
- **Word (.docx):** `docx-preview` (schneller, besser Layout als Mammoth) oder weiter Mammoth + Styling; offline, OSS.
- **Excel (.xlsx):** `SheetJS (xlsx)` + `sheet_to_html` mit Sheet-Tabs UI, oder `Luckysheet` (nur View-Mode) als Alternative; SheetJS bleibt schlank.
- **Text/Markdown:** Native `<pre>` für txt; `marked` + `highlight.js` für md mit Syntax-Highlighting.

### API-Design
- `/api/projects/{id}/documents` sollte liefern:
  - `original_url`, `annotated_url` (falls vorhanden), `format`, `pages` (wenn bekannt), `default_page`, `id`.
- Download/stream endpoints setzen korrekten `Content-Type` und `Content-Disposition: inline` für PDF, sonst attachment.
- Optional: `/api/projects/{id}/documents/{filename}/meta` → Seitenanzahl, md5 für cache-busting, annotated pairing.
- Chat-Links geben `{ filename, page, view }` zurück; Frontend mappt direkt.

### Code-Beispiel (Pseudo-Code)
```jsx
<DocumentViewer
  documentId={doc.id}
  filename={doc.filename}
  format={doc.format}
  annotated={viewMode === 'annotated'}
  page={targetPage}
  onPageChange={(p) => setPage(p)}
  sourceUrl={viewMode === 'annotated' ? doc.annotated_url : doc.original_url}
/>
```

## 4. Implementierungs-Plan
### Phase 1: Cleanup (Alte Bugs fixen)
- [ ] Entferne verwaiste `viewer_content.html` Toolbar/Canvas oder verbinde sie mit PDF.js Renderpfad.
- [ ] Implementiere `renderPdf`-Pfad verbindlich, entferne iframe-Fallback; nutze AbortController bei fetches.
- [ ] Liefere aus `/api/projects/{id}/documents` `annotated_file/annotated_url` damit Toggle ohne Raten funktioniert.
- [ ] Auto-Open erstes Dokument nach Sidebar-Load; handle fehlende Auswahl.

### Phase 2: Refactoring (Robust machen)
- [ ] Baue Viewer-Shell + Renderer (PDF, DOCX, XLSX, TEXT) mit dispose/abort.
- [ ] Deep-Linking (Query params) und Chat-Source Handler, inkl. `page` Jump für PDF.
- [ ] Excel: Sheet-Tabs (iterate SheetNames) und sichere Table-Styles; Word: docx-preview; Markdown: marked+highlight.js.
- [ ] Annotated/Original Toggle nutzt exakte URLs aus API, mit sofortigem Reload und Loading-State.

### Phase 3: Testing (Alle Use Cases)
- [ ] UC1: Sidebar Open (PDF/DOCX/XLSX/TXT) – snapshot/E2E.
- [ ] UC2: Dokumentwechsel – ensure dispose/abort works.
- [ ] UC3: Chat-Quelle Link → page jump verified.
- [ ] UC4: Original/Annotiert Toggle – both existing; 404 guarded.
- [ ] UC5: First document auto-open.
- [ ] UC6: PDF goto page (programmatic call) – assert scroll/zoom.

## 5. Testing-Strategie
- **Unit:** Renderer functions (pdf load, docx convert, xlsx sheet selection) with mocked fetch/ArrayBuffer.
- **Integration:** Simulate document switching with fake endpoints; ensure abort cancels prior fetch.
- **E2E:** Playwright/Cypress flows for UC1–UC6; mock API to provide annotated/original URLs; verify page jump.
- **Perf:** Load 50+ page PDF; measure switch time <2s; ensure no memory leaks (dispose called).

## 6. Offene Fragen
- Sollen Annotated-Files für non-PDF (docx/xlsx) unterstützt werden, und wie werden sie benannt? API-Feld nötig.
- Gibt es Server-seitige Signed URLs oder Auth-Zwang, der iframe/Blob-URLs betrifft?
- Soll der Viewer innerhalb bestehender Template-Architektur bleiben oder mittelfristig auf React/SPA migrieren?
- Muss der Chat-Link „Quelle“ Format-info (pdf vs docx) mitliefern oder reicht filename + page?
