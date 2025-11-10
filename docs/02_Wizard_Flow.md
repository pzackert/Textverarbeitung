# Wizard-Flow
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 3.0  
**Stand:** 10. November 2025

---

## 🎯 ÜBERSICHT

Der Wizard führt Benutzer **Step-by-Step** durch die automatisierte Antragsprüfung. Jeder Schritt baut auf dem vorherigen auf und ist klar abgegrenzt.

### Prozess-Flow

```
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Schritt 0: Projektübersicht                        │
│  → Bestehendes Projekt öffnen ODER neu anlegen      │
│                                                      │
└──────────────────────┬───────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Schritt 1: Projekt anlegen                         │
│  → Metadaten erfassen (Name, Firma, Modul)          │
│                                                      │
└──────────────────────┬───────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Schritt 2: Dokumente hochladen                     │
│  → Projektskizze + Projektantrag hochladen          │
│                                                      │
└──────────────────────┬───────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Schritt 3: Automatische Verarbeitung               │
│  → Parsing → RAG-Aufbau → Kriterienprüfung          │
│                                                      │
└──────────────────────┬───────────────────────────────┘
                       ↓
┌─────────────────────────────────────────────────────┐
│                                                      │
│  Schritt 4: Ergebnisübersicht                       │
│  → Prüfungsergebnisse anzeigen & exportieren        │
│                                                      │
└─────────────────────────────────────────────────────┘
```


---

## 📋 SCHRITT 0: PROJEKTÜBERSICHT

**Zweck:** Einstiegspunkt der Anwendung - Überblick über alle Projekte

### Was passiert hier?
- Anzeige aller angelegten Projekte in tabellarischer Form
- Status-Übersicht (Neu, In Bearbeitung, Abgeschlossen)
- Navigation zu bestehenden Projekten
- Button zum Anlegen eines neuen Projekts

### Output
- User wählt bestehendes Projekt ODER legt neues an

**UI-Details:** Siehe `01_UI_FLOW.md` → Seite 0

---

## 📋 SCHRITT 1: PROJEKT ANLEGEN

**Zweck:** Grunddaten des Förderprojekts erfassen

### Was passiert hier?
- User gibt Projekt-Metadaten ein:
  - Projektname
  - Antragsteller/Firma
  - Fördermodul (PROFI Standard, Transfer, etc.)
  - Projektart (Forschung, Entwicklung, Studie)
  
### Backend-Aktion
System erstellt automatisch:
- Projekt-ID (eindeutig)
- Ordnerstruktur im Dateisystem
- `metadata.json` mit Projekt-Informationen

### Output
- Projekt ist angelegt und bereit für Dokumenten-Upload
- User wird zu Schritt 2 weitergeleitet

**Datenstruktur:** Siehe `06_DATA_MANAGEMENT.md`  
**UI-Details:** Siehe `01_UI_FLOW.md` → Seite 1

---

## 📋 SCHRITT 2: DOKUMENTE HOCHLADEN

**Zweck:** Alle erforderlichen Dokumente in das System laden

### Was passiert hier?
User lädt 2 Haupt-Dokumente hoch:

1. **Projektskizze** (2-3 Seiten)
   - Format: PDF oder DOCX
   - Enthält: Projektbeschreibung, Marktanalyse, etc.

2. **Projektantrag** (Formular + Anhänge)
   - Format: PDF oder DOCX
   - Enthält: Strukturierte Antragsdaten

Optional: Weitere Dokumente (Lebensläufe, Letters of Intent, etc.)

### Backend-Aktion
- Dateien werden im Projekt-Ordner gespeichert
- Metadaten werden aktualisiert (Dateiname, Größe, Upload-Zeit)
- Dateityp-Validierung

### Output
- Alle Dokumente sind hochgeladen
- System ist bereit für automatische Verarbeitung
- User wird zu Schritt 3 weitergeleitet

**Parsing-Details:** Siehe `02_DOCUMENT_PARSING.md`  
**UI-Details:** Siehe `01_UI_FLOW.md` → Seite 2

---

## 📋 SCHRITT 3: AUTOMATISCHE VERARBEITUNG

**Zweck:** Dokumente analysieren und Kriterien prüfen

### Was passiert hier?

#### Phase 3.1: Parsing
- System extrahiert Text aus allen hochgeladenen Dokumenten
- Strukturdaten werden erkannt (Überschriften, Tabellen, etc.)
- Status-Anzeige: "Parsing läuft..."

#### Phase 3.2: RAG-Aufbau
- Texte werden in Chunks aufgeteilt
- Embeddings werden generiert
- ChromaDB wird mit Vektoren befüllt
- Status-Anzeige: "RAG-Index wird erstellt..."

#### Phase 3.3: Kriterienprüfung
LLM prüft sukzessive alle 6 Förderkriterien:

1. **K001: Projektort** - Betriebsstätte in Hamburg?
2. **K002: Unternehmensalter** - Min. 2 Jahre?
3. **K003: Projektbeginn** - Noch nicht begonnen?
4. **K004: Projektziel** - Neue/verbesserte Produkte?
5. **K005: Finanzierung** - 10k-100k EUR, gesichert?
6. **K006: Erfolgsaussicht** - Ohne Förderung nicht realisierbar?

Für jedes Kriterium:
- RAG findet relevante Textstellen
- LLM bewertet: Erfüllt / Nicht erfüllt / Unklar
- Begründung wird generiert
- Status wird live aktualisiert

### UI-Verhalten während Verarbeitung

**Oberer Bereich:** Prozess-Status
```
⏳ Parsing...        ✓ Abgeschlossen
⏳ RAG-Aufbau...     ⏳ 45% (23/50 Chunks)
⏹  LLM-Prüfung      ⏹ Wartet...
```

**Unterer Bereich:** Kriterienliste (Live-Updates)
```
┌────────────────────────────────────────────────┐
│ Kriterium              │ Status  │ Konfidenz  │
├────────────────────────────────────────────────┤
│ K001: Projektort       │ ✓       │ 95%        │
│ K002: Unternehmensalter│ ✓       │ 88%        │
│ K003: Projektbeginn    │ ⏳      │ -          │
│ K004: Projektziel      │ ⏹      │ -          │
│ K005: Finanzierung     │ ⏹      │ -          │
│ K006: Erfolgsaussicht  │ ⏹      │ -          │
└────────────────────────────────────────────────┘
```

### Backend-Aktionen
- Parser-Module verarbeiten Dokumente
- RAG-System indexiert Inhalte
- Criteria-Engine führt LLM-Checks durch
- Ergebnisse werden in `metadata.json` gespeichert

### Output
- Alle Kriterien sind geprüft (✓, ✗, oder ⚠️)
- Detaillierte Begründungen für jedes Kriterium
- System wechselt automatisch zu Schritt 4

**Parsing-Details:** Siehe `02_DOCUMENT_PARSING.md`  
**RAG-Details:** Siehe `03_RAG_SYSTEM.md`  
**Kriterien-Details:** Siehe `05_CRITERIA_ENGINE.md`  
**UI-Details:** Siehe `01_UI_FLOW.md` → Seite 3

---

## 📋 SCHRITT 4: ERGEBNISÜBERSICHT

**Zweck:** Prüfungsergebnisse präsentieren und exportieren

### Was passiert hier?

#### Zusammenfassung
```
Prüfung abgeschlossen: 5 von 6 Kriterien erfüllt

✓ K001: Projektort Hamburg
✓ K002: Unternehmensalter
✗ K003: Projektbeginn (bereits begonnen)
✓ K004: Projektziel  
✓ K005: Finanzierung
✓ K006: Erfolgsaussicht
```

#### Detailansicht
Für jedes Kriterium:
- Status (Erfüllt / Nicht erfüllt)
- Begründung (aus LLM-Analyse)
- Quellen (relevante Dokumenten-Abschnitte)
- Konfidenz-Score
- Option zur manuellen Korrektur

#### Export-Funktionen
User kann Ergebnisse exportieren als:
- **PDF** - Druckfähiger Prüfbericht
- **JSON** - Maschinenlesbare Daten
- **Markdown** - Text-Format für Weiterverarbeitung

### Backend-Aktion
- Report-Generator erstellt strukturierte Ausgabe
- Export-Files werden im Results-Ordner gespeichert

### Output
- Vollständige Dokumentation der Prüfung
- Downloadbare Reports
- Projekt-Status wird auf "Abgeschlossen" gesetzt

**UI-Details:** Siehe `01_UI_FLOW.md` → Seite 4

---

## 🔄 WIZARD-NAVIGATION

### Vorwärts-Navigation
Jeder Schritt hat einen "Weiter"-Button, der erst aktiviert wird, wenn:
- Alle erforderlichen Daten eingegeben sind (Schritt 1)
- Alle Pflichtdokumente hochgeladen sind (Schritt 2)
- Die Verarbeitung abgeschlossen ist (Schritt 3)

### Rückwärts-Navigation
User kann jederzeit zu vorherigen Schritten zurück:
- Projektdaten anpassen
- Dokumente austauschen
- Prüfung neu durchführen

### Projekt speichern
Nach jedem Schritt wird der Projekt-Zustand automatisch gespeichert:
- User kann Anwendung schließen und später fortsetzen
- Letzter Status wird in `metadata.json` festgehalten

---

## 🎯 GESAMTABLAUF (ZUSAMMENFASSUNG)

```
Schritt 0: Projektübersicht
  → Projekt auswählen oder neu anlegen
  
Schritt 1: Projekt anlegen
  → Metadaten erfassen
  → Ordnerstruktur wird erstellt
  
Schritt 2: Dokumente hochladen
  → Projektskizze + Projektantrag
  → Dateien werden gespeichert
  
Schritt 3: Automatische Verarbeitung
  → Parsing (Text extrahieren)
  → RAG-Aufbau (Vektoren indexieren)
  → Kriterienprüfung (6 Checks nacheinander)
  → Live-Status-Updates in UI
  
Schritt 4: Ergebnisübersicht
  → Zusammenfassung (x/6 erfüllt)
  → Detaillierte Begründungen
  → Export (PDF, JSON, Markdown)
```

**Geschätzte Dauer:** 5-10 Minuten pro Projekt

---

## 📚 VERWANDTE DOKUMENTE

- **UI-Implementierung:** `01_UI_FLOW.md`
- **Dokumenten-Parsing:** `02_DOCUMENT_PARSING.md`
- **RAG-System:** `03_RAG_SYSTEM.md`
- **LLM-Integration:** `04_LLM_INTEGRATION.md`
- **Kriterien-Engine:** `05_CRITERIA_ENGINE.md`
- **Datenmanagement:** `06_DATA_MANAGEMENT.md`

---

**Ende der Wizard-Flow Dokumentation**
                
                st.success(f"✅ Erfolgreich geparst")
                st.json(parse_result["metadata"])
                
                # Metadaten aktualisieren
                doc["parsed"] = True
                doc["parsed_at"] = datetime.now().isoformat()
                
            except Exception as e:
                st.error(f"❌ Fehler: {str(e)}")
        
        parsed_count += 1
        progress_bar.progress(parsed_count / total_docs)

# Speichern
save_projekt_metadata(projekt_id, metadata)
metadata["checks_completed"]["parsing"] = True

status_text.text("✅ Alle Dokumente geparst!")

# Weiter-Button
if st.button("➡️ Weiter zu Schritt 4: Informationsextraktion"):
    st.switch_page("pages/4_Extraktion.py")
```

### Backend-Logik

```python
# backend/parsers/parser_factory.py

from pathlib import Path
from .pdf_parser import PDFParser
from .docx_parser import DOCXParser
from .xlsx_parser import XLSXParser

def parse_document(projekt_id: str, doc_type: str) -> dict:
    """Wählt richtigen Parser und parst Dokument."""
    
    # 1. Dokument finden
    metadata = load_projekt_metadata(projekt_id)
    doc = next(d for d in metadata["documents"] if d["doc_type"] == doc_type)
    
    file_path = Path(f"data/projects/{projekt_id}/uploads/{doc['filename']}")
    
    # 2. Parser wählen
    suffix = file_path.suffix.lower()
    
    if suffix == ".pdf":
        parser = PDFParser()
    elif suffix == ".docx":
        parser = DOCXParser()
    elif suffix in [".xlsx", ".xls"]:
        parser = XLSXParser()
    else:
        raise ValueError(f"Unsupported file format: {suffix}")
    
    # 3. Parsen
    result = parser.parse(file_path)
    
    # 4. Extrahierte Daten speichern
    extracted_path = Path(f"data/projects/{projekt_id}/extracted/{doc_type}.json")
    with open(extracted_path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    
    return result
```

### Output
- Geparste Daten in `data/projects/projekt_XXX/extracted/`
- Eine JSON-Datei pro Dokument

---

## SCHRITT 4: INFORMATIONSEXTRAKTION (RAG)

### Ziel
Strukturierte Informationen aus den Dokumenten extrahieren und in ChromaDB indexieren.

### UI-Elemente (Streamlit)

```python
# frontend/pages/4_Extraktion.py

import streamlit as st

st.title("📊 Informationsextraktion")

projekt_id = st.session_state.get("current_projekt_id")
metadata = load_projekt_metadata(projekt_id)

st.info("🤖 LLM extrahiert strukturierte Daten aus den Dokumenten...")

# RAG-Pipeline starten
with st.spinner("Dokumente werden in Vector-DB indexiert..."):
    # 1. Alle extrahierten Texte laden
    extracted_texts = load_all_extracted_texts(projekt_id)
    
    # 2. Chunking
    chunks = chunk_texts(extracted_texts)
    st.write(f"✅ {len(chunks)} Text-Chunks erstellt")
    
    # 3. Embeddings erstellen
    embeddings = create_embeddings(chunks)
    st.write(f"✅ Embeddings erstellt")
    
    # 4. In ChromaDB speichern
    vector_ids = store_in_chromadb(projekt_id, chunks, embeddings)
    st.write(f"✅ {len(vector_ids)} Chunks in Vector-DB gespeichert")

# Strukturierte Extraktion
st.subheader("🔍 Strukturierte Datenextraktion")

with st.spinner("LLM extrahiert strukturierte Felder..."):
    extracted_data = extract_structured_data(projekt_id)

# Anzeige extrahierter Daten
col1, col2 = st.columns(2)

with col1:
    st.metric("Projektlaufzeit", f"{extracted_data['projekt_details']['laufzeit_monate']} Monate")
    st.metric("Gesamtkosten", f"{extracted_data['projekt_details']['gesamtkosten']:,.2f} €")

with col2:
    st.metric("Beantragte Förderung", f"{extracted_data['projekt_details']['beantragte_foerderung']:,.2f} €")
    st.metric("Förderquote", f"{extracted_data['projekt_details']['foerderquote']*100:.1f}%")

# Unternehmensdaten
st.subheader("🏢 Unternehmensdaten")
st.write(f"**Name:** {extracted_data['unternehmen']['name']}")
st.write(f"**Mitarbeiter:** {extracted_data['unternehmen']['mitarbeiter']}")
st.write(f"**Standort:** {extracted_data['unternehmen']['standort']['ort']}")
st.write(f"**KMU-Status:** {'✅ Ja' if extracted_data['unternehmen']['kmu_status']['ist_kmu'] else '❌ Nein'}")

# Personalkosten-Tabelle
st.subheader("👥 Personalkosten")
import pandas as pd

personal_df = pd.DataFrame(extracted_data['personalkosten']['mitarbeiter'])
st.dataframe(personal_df[['rolle', 'abschluss', 'personenmonate', 'kosten_gesamt']])

# Speichern
metadata["extracted_data"] = extracted_data
metadata["checks_completed"]["extraction"] = True
save_projekt_metadata(projekt_id, metadata)

st.success("✅ Informationsextraktion abgeschlossen!")

# Weiter-Button
if st.button("➡️ Weiter zu Schritt 5: Fördervoraussetzungen prüfen"):
    st.switch_page("pages/5_Foerdervoraussetzungen.py")
```

### Backend-Logik

```python
# backend/rag/extractor.py

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import HuggingFaceEmbeddings
from langchain.vectorstores import Chroma

def chunk_texts(texts: dict) -> list:
    """Chunked Texte für RAG."""
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    
    chunks = []
    for doc_type, text in texts.items():
        doc_chunks = text_splitter.split_text(text)
        
        for i, chunk in enumerate(doc_chunks):
            chunks.append({
                "text": chunk,
                "metadata": {
                    "doc_type": doc_type,
                    "chunk_index": i
                }
            })
    
    return chunks

def store_in_chromadb(projekt_id: str, chunks: list, embeddings) -> list:
    """Speichert Chunks in ChromaDB."""
    
    vectorstore = Chroma(
        collection_name=f"projekt_{projekt_id}",
        embedding_function=embeddings,
        persist_directory="data/chromadb"
    )
    
    texts = [c["text"] for c in chunks]
    metadatas = [c["metadata"] for c in chunks]
    
    vector_ids = vectorstore.add_texts(texts, metadatas=metadatas)
    
    return vector_ids

def extract_structured_data(projekt_id: str) -> dict:
    """Extrahiert strukturierte Daten mit LLM."""
    
    # RAG-Retriever initialisieren
    retriever = get_retriever(projekt_id)
    llm = get_lm_studio_client()
    
    # Verschiedene Extraktion-Tasks
    projekt_details = extract_projekt_details(retriever, llm)
    unternehmen = extract_unternehmen_data(retriever, llm)
    personalkosten = extract_personalkosten(retriever, llm)
    
    return {
        "projekt_details": projekt_details,
        "unternehmen": unternehmen,
        "personalkosten": personalkosten
    }
```

### Output
- Chunks in ChromaDB indexiert
- Strukturierte Daten in `metadata.json` unter `extracted_data`

---

## SCHRITT 5: FÖRDERVORAUSSETZUNGEN PRÜFEN

### Ziel
Alle 6 Fördervoraussetzungen prüfen und Checkliste erstellen.

### UI-Elemente (Streamlit)

```python
# frontend/pages/5_Foerdervoraussetzungen.py

import streamlit as st

st.title("✅ Fördervoraussetzungen prüfen")

projekt_id = st.session_state.get("current_projekt_id")
metadata = load_projekt_metadata(projekt_id)

st.subheader("🔍 Automatische Prüfung läuft...")

# Prüfung durchführen
with st.spinner("LLM prüft Fördervoraussetzungen..."):
    check_results = check_foerdervoraussetzungen(projekt_id)

# Ergebnisse anzeigen
for i, (key, result) in enumerate(check_results.items(), 1):
    with st.expander(f"{i}. {result['kriterium']}", expanded=True):
        
        # Status
        if result['erfuellt']:
            st.success(f"✅ Erfüllt")
        else:
            st.error(f"❌ Nicht erfüllt")
        
        # Details
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.write("**Wert:**")
            st.code(result['wert'])
        
        with col2:
            st.write("**Begründung:**")
            st.write(result['begruendung'])
        
        # Quellen
        st.write("**Quellen:**")
        for source in result['quellen']:
            st.write(f"- {source}")
        
        # Confidence
        st.progress(result['confidence'])
        st.caption(f"Confidence: {result['confidence']*100:.0f}%")

# Gesamtergebnis
alle_erfuellt = all(r['erfuellt'] for r in check_results.values())

st.divider()

if alle_erfuellt:
    st.success("✅ **Alle Fördervoraussetzungen erfüllt!**")
else:
    st.error("❌ **Nicht alle Fördervoraussetzungen erfüllt.**")
    nicht_erfuellt = [r['kriterium'] for r in check_results.values() if not r['erfuellt']]
    st.warning(f"Nicht erfüllt: {', '.join(nicht_erfuellt)}")

# Checkliste herunterladen
checkliste_md = generate_checkliste_markdown(check_results)
st.download_button(
    label="📥 Checkliste als Markdown herunterladen",
    data=checkliste_md,
    file_name=f"foerdervoraussetzungen_{projekt_id}.md",
    mime="text/markdown"
)

# Speichern
metadata["pruefung"] = {
    "foerdervoraussetzungen": check_results,
    "alle_erfuellt": alle_erfuellt,
    "geprueft_am": datetime.now().isoformat()
}
metadata["checks_completed"]["foerdervoraussetzungen"] = True
save_projekt_metadata(projekt_id, metadata)

# Weiter-Button
if st.button("➡️ Weiter zu Schritt 6: Bewertung"):
    st.switch_page("pages/6_Bewertung.py")
```

### Backend-Logik

```python
# backend/rules/foerdervoraussetzungen.py

def check_foerdervoraussetzungen(projekt_id: str) -> dict:
    """Führt alle 6 Checks durch."""
    
    retriever = get_retriever(projekt_id)
    llm = get_lm_studio_client()
    
    return {
        "projektort": check_projektort(retriever, llm, projekt_id),
        "unternehmensalter": check_unternehmensalter(retriever, llm, projekt_id),
        "projektbeginn": check_projektbeginn(retriever, llm, projekt_id),
        "projektziel": check_projektziel(retriever, llm, projekt_id),
        "finanzierung": check_finanzierung(retriever, llm, projekt_id),
        "erfolgsaussicht": check_erfolgsaussicht(retriever, llm, projekt_id)
    }

def check_projektort(retriever, llm, projekt_id: str) -> dict:
    """Prüft: Betriebsstätte in Hamburg?"""
    
    # 1. RAG: Relevante Dokumente
    docs = retriever.invoke(
        "Betriebsstätte Hamburg Standort Adresse Handelsregister"
    )
    
    # 2. LLM-Check
    prompt = f"""Prüfe anhand der folgenden Dokumente: Hat das Unternehmen eine Betriebsstätte in Hamburg?

Dokumente:
{'\n\n'.join([d.page_content for d in docs[:3]])}

Antworte im JSON-Format:
{{
    "hat_betriebsstätte": true/false,
    "adresse": "Vollständige Adresse",
    "begruendung": "Kurze Begründung",
    "confidence": 0.95
}}"""
    
    response = llm.invoke(prompt)
    result = json.loads(response)
    
    return {
        "kriterium": "Projektort in Hamburg",
        "erfuellt": result["hat_betriebsstätte"],
        "wert": result["adresse"],
        "begruendung": result["begruendung"],
        "quellen": [d.metadata.get("source", "unknown") for d in docs],
        "confidence": result["confidence"]
    }

# ... analog für die anderen 5 Checks
```

### Output
- Prüfergebnisse in `metadata.json` unter `pruefung.foerdervoraussetzungen`
- Checkliste als Markdown-Download

---

## SCHRITT 6: BEWERTUNG DURCHFÜHREN

### Ziel
Projekt nach 5 Bewertungskriterien bewerten und Scoring durchführen.

### UI-Elemente (Streamlit)

```python
# frontend/pages/6_Bewertung.py

import streamlit as st
import plotly.graph_objects as go

st.title("🌟 Bewertung nach Kriterien")

projekt_id = st.session_state.get("current_projekt_id")
metadata = load_projekt_metadata(projekt_id)

st.subheader("🤖 LLM bewertet das Projekt...")

# Bewertung durchführen
with st.spinner("Bewertung läuft..."):
    bewertung = bewerten_projekt(projekt_id)

# Radar-Chart
st.subheader("📊 Bewertungsprofil")

categories = [
    "Produktidee",
    "Innovationsgrad",
    "Team",
    "Vermarktung",
    "Arbeitsplatz/Umwelt"
]

values = [
    bewertung["produktidee"]["score"],
    bewertung["innovationsgrad"]["score"],
    bewertung["team"]["score"],
    bewertung["vermarktung"]["score"],
    bewertung["arbeitsplatz_umwelt"]["score"]
]

fig = go.Figure()
fig.add_trace(go.Scatterpolar(
    r=values,
    theta=categories,
    fill='toself',
    name='Bewertung'
))

fig.update_layout(
    polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
    showlegend=False,
    height=500
)

st.plotly_chart(fig, use_container_width=True)

# Einzelne Kriterien
st.subheader("📋 Detaillierte Bewertung")

for i, (key, result) in enumerate(bewertung.items(), 1):
    with st.expander(f"{i}. {key.replace('_', ' ').title()}", expanded=False):
        
        # Score
        st.metric(
            "Score",
            f"{result['score']}/100",
            delta=f"{result['score'] - 75} vs. Durchschnitt"
        )
        
        # Begründung
        st.write("**Begründung:**")
        st.write(result['begruendung'])
        
        # Stärken
        st.write("**Stärken:**")
        for staerke in result['staerken']:
            st.write(f"✅ {staerke}")
        
        # Schwächen
        st.write("**Schwächen:**")
        for schwaeche in result['schwaechen']:
            st.write(f"⚠️ {schwaeche}")

# Gesamtbewertung
st.divider()

gesamtscore = sum(
    result['score'] * result.get('gewichtung', 0.2)
    for result in bewertung.values()
)

col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Gesamtscore", f"{gesamtscore:.1f}/100")

with col2:
    if gesamtscore >= 80:
        note = "Sehr gut"
        color = "green"
    elif gesamtscore >= 65:
        note = "Gut"
        color = "green"
    elif gesamtscore >= 50:
        note = "Befriedigend"
        color = "orange"
    else:
        note = "Unzureichend"
        color = "red"
    
    st.metric("Gesamtnote", note)

with col3:
    if gesamtscore >= 65:
        empfehlung = "✅ Aufforderung"
    elif gesamtscore >= 50:
        empfehlung = "⚠️ Überarbeitung"
    else:
        empfehlung = "❌ Ablehnung"
    
    st.metric("Empfehlung", empfehlung)

# Speichern
metadata["bewertung"] = bewertung
metadata["gesamtscore"] = gesamtscore
metadata["empfehlung"] = empfehlung
metadata["checks_completed"]["bewertung"] = True
save_projekt_metadata(projekt_id, metadata)

# Weiter-Button
if st.button("➡️ Weiter zu Schritt 7: Report generieren"):
    st.switch_page("pages/7_Report.py")
```

### Backend-Logik

```python
# backend/rules/bewertung.py

def bewerten_projekt(projekt_id: str) -> dict:
    """Bewertet Projekt nach 5 Kriterien."""
    
    retriever = get_retriever(projekt_id)
    llm = get_lm_studio_client()
    
    return {
        "produktidee": bewerte_produktidee(retriever, llm),
        "innovationsgrad": bewerte_innovationsgrad(retriever, llm),
        "team": bewerte_team(retriever, llm),
        "vermarktung": bewerte_vermarktung(retriever, llm),
        "arbeitsplatz_umwelt": bewerte_arbeitsplatz_umwelt(retriever, llm)
    }

def bewerte_produktidee(retriever, llm) -> dict:
    """Bewertet Produktidee (0-100 Punkte)."""
    
    # RAG
    docs = retriever.invoke(
        "Produktidee Innovation Alleinstellungsmerkmal Wettbewerbsvorteil Kundennutzen"
    )
    
    # LLM-Bewertung
    prompt = f"""Bewerte die PRODUKTIDEE nach folgenden Kriterien (0-100 Punkte):
1. Verbesserungen gegenüber bestehenden Lösungen
2. Alleinstellungsmerkmale / Wettbewerbsvorteile
3. Kundennutzen

Dokumente:
{'\n\n'.join([d.page_content for d in docs[:5]])}

Antworte im JSON-Format:
{{
    "score": 87,
    "gewichtung": 0.20,
    "begruendung": "Detaillierte Begründung...",
    "staerken": ["Stärke 1", "Stärke 2"],
    "schwaechen": ["Schwäche 1", "Schwäche 2"]
}}"""
    
    response = llm.invoke(prompt)
    return json.loads(response)

# ... analog für die anderen 4 Kriterien
```

### Output
- Bewertungsergebnisse in `metadata.json` unter `bewertung`
- Gesamtscore & Empfehlung

---

## SCHRITT 7: REPORT & CHECKLISTE GENERIEREN

### Ziel
Abschlussreport und Checklisten als Markdown/PDF exportieren.

### UI-Elemente (Streamlit)

```python
# frontend/pages/7_Report.py

import streamlit as st

st.title("📄 Report & Checkliste generieren")

projekt_id = st.session_state.get("current_projekt_id")
metadata = load_projekt_metadata(projekt_id)

st.success("✅ Alle Prüfungen abgeschlossen!")

# Report-Optionen
st.subheader("📋 Report-Optionen")

report_typ = st.radio(
    "Report-Typ:",
    ["Vollständiger Bewertungsbericht", "Fördervoraussetzungen-Checkliste", "Beides"]
)

format_option = st.radio(
    "Format:",
    ["Markdown (.md)", "PDF", "Beides"]
)

# Generieren
if st.button("📥 Report generieren"):
    
    with st.spinner("Report wird erstellt..."):
        
        # Markdown-Reports
        if report_typ in ["Vollständiger Bewertungsbericht", "Beides"]:
            bewertungsbericht = generate_bewertungsbericht_markdown(metadata)
            
            st.download_button(
                label="📥 Bewertungsbericht herunterladen",
                data=bewertungsbericht,
                file_name=f"bewertungsbericht_{projekt_id}.md",
                mime="text/markdown"
            )
        
        if report_typ in ["Fördervoraussetzungen-Checkliste", "Beides"]:
            checkliste = generate_checkliste_markdown(metadata['pruefung']['foerdervoraussetzungen'])
            
            st.download_button(
                label="📥 Checkliste herunterladen",
                data=checkliste,
                file_name=f"checkliste_{projekt_id}.md",
                mime="text/markdown"
            )
        
        # Optional: PDF-Generierung
        if "PDF" in format_option:
            st.info("💡 PDF-Generierung noch nicht implementiert. Nutzen Sie Markdown → PDF-Converter.")

# Vorschau
st.subheader("👁️ Vorschau: Bewertungsbericht")

with st.expander("Markdown-Vorschau", expanded=True):
    preview = generate_bewertungsbericht_markdown(metadata)
    st.markdown(preview)

# Projekt abschließen
st.divider()

if st.button("🎉 Projekt abschließen"):
    metadata["status"] = "completed"
    metadata["completed_at"] = datetime.now().isoformat()
    save_projekt_metadata(projekt_id, metadata)
    
    st.success("✅ Projekt abgeschlossen!")
    st.balloons()
```

### Backend-Logik

```python
# backend/report_generator.py

def generate_bewertungsbericht_markdown(metadata: dict) -> str:
    """Generiert Bewertungsbericht als Markdown."""
    
    projekt_name = metadata['projekt_name']
    antragsteller = metadata['antragsteller']
    bewertung = metadata['bewertung']
    gesamtscore = metadata['gesamtscore']
    empfehlung = metadata['empfehlung']
    
    md = f"""# Bewertungsbericht

## Projekt: {projekt_name}

**Antragsteller:** {antragsteller}  
**Fördermodul:** {metadata['modul']}  
**Erstellt am:** {datetime.now().strftime('%d.%m.%Y %H:%M')}

---

## Executive Summary

**Gesamtbewertung:** {gesamtscore:.1f}/100 Punkte  
**Empfehlung:** {empfehlung}

### Top 3 Stärken:
"""
    
    # Stärken sammeln
    alle_staerken = []
    for kriterium, details in bewertung.items():
        alle_staerken.extend(details['staerken'])
    
    for i, staerke in enumerate(alle_staerken[:3], 1):
        md += f"{i}. {staerke}\n"
    
    md += "\n### Top 3 Verbesserungspotenziale:\n"
    
    # Schwächen sammeln
    alle_schwaechen = []
    for kriterium, details in bewertung.items():
        alle_schwaechen.extend(details['schwaechen'])
    
    for i, schwaeche in enumerate(alle_schwaechen[:3], 1):
        md += f"{i}. {schwaeche}\n"
    
    # Fördervoraussetzungen
    md += "\n---\n\n## Fördervoraussetzungen\n\n"
    md += "| Kriterium | Status | Begründung |\n"
    md += "|-----------|--------|------------|\n"
    
    for key, result in metadata['pruefung']['foerdervoraussetzungen'].items():
        status = "✅ Erfüllt" if result['erfuellt'] else "❌ Nicht erfüllt"
        md += f"| {result['kriterium']} | {status} | {result['begruendung']} |\n"
    
    # Bewertungskriterien
    md += "\n---\n\n## Bewertung nach Kriterien\n\n"
    
    for key, details in bewertung.items():
        md += f"### {key.replace('_', ' ').title()}\n\n"
        md += f"**Score:** {details['score']}/100\n\n"
        md += f"**Begründung:** {details['begruendung']}\n\n"
        
        md += "**Stärken:**\n"
        for staerke in details['staerken']:
            md += f"- {staerke}\n"
        
        md += "\n**Schwächen:**\n"
        for schwaeche in details['schwaechen']:
            md += f"- {schwaeche}\n"
        
        md += "\n"
    
    md += "\n---\n\n## Fazit\n\n"
    md += f"Das Projekt '{projekt_name}' erreicht eine Gesamtbewertung von {gesamtscore:.1f}/100 Punkten.\n\n"
    md += f"**Empfehlung:** {empfehlung}\n"
    
    return md

def generate_checkliste_markdown(check_results: dict) -> str:
    """Generiert Fördervoraussetzungen-Checkliste als Markdown."""
    
    md = "# Fördervoraussetzungen - Checkliste\n\n"
    md += "| # | Kriterium | Status | Wert | Begründung |\n"
    md += "|---|-----------|--------|------|------------|\n"
    
    for i, (key, result) in enumerate(check_results.items(), 1):
        status = "✅" if result['erfuellt'] else "❌"
        md += f"| {i} | {result['kriterium']} | {status} | {result['wert']} | {result['begruendung']} |\n"
    
    return md
```

### Output
- Markdown-Reports als Download
- Optional: PDFs
- Projekt-Status auf "completed"

---

## ZUSAMMENFASSUNG

**Wizard-Flow komplett:**
1. ✅ Projekt anlegen → Metadaten erfassen
2. ✅ Dokumente hochladen → Dateien speichern
3. ✅ Parsing → Text/Daten extrahieren
4. ✅ RAG-Indexierung → ChromaDB befüllen + strukturierte Extraktion
5. ✅ Fördervoraussetzungen → 6 Checks + Checkliste
6. ✅ Bewertung → 5 Kriterien + Scoring
7. ✅ Report → Markdown-Export

**Gesamtdauer (geschätzt):** 5-10 Minuten pro Projekt

**Ende der Wizard-Flow Dokumentation**
