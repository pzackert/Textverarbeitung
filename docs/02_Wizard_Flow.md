# Wizard-Flow: Schritt-für-Schritt
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 2.0  
**Stand:** 31. Oktober 2024

---

## ÜBERSICHT: 7-SCHRITTE-WIZARD

```
1. Projekt anlegen
   ↓
2. Dokumente hochladen
   ↓
3. Dokumente parsen
   ↓
4. Informationsextraktion (RAG)
   ↓
5. Fördervoraussetzungen prüfen
   ↓
6. Bewertung durchführen
   ↓
7. Report & Checkliste generieren
```

---

## SCHRITT 1: PROJEKT ANLEGEN

### Ziel
Neues Förderprojekt im System anlegen und grundlegende Metadaten erfassen.

### UI-Elemente (Streamlit)

```python
# frontend/pages/1_Projekt_anlegen.py

import streamlit as st
from datetime import datetime
from pathlib import Path
import json

st.title("🆕 Neues Projekt anlegen")

# Form
with st.form("projekt_form"):
    projekt_name = st.text_input(
        "Projektname *",
        placeholder="z.B. Vollautomatische Verpackungsmaschine"
    )
    
    antragsteller = st.text_input(
        "Antragsteller (Unternehmen) *",
        placeholder="z.B. Verpackungsmaschinenbau GmbH"
    )
    
    modul = st.selectbox(
        "Fördermodul *",
        [
            "PROFI Standard",
            "PROFI Transfer",
            "PROFI Transfer Plus (EFRE)",
            "PROFI Umwelt",
            "PROFI Umwelt Transfer"
        ]
    )
    
    projektart = st.selectbox(
        "Projektart *",
        [
            "Industrielle Forschung",
            "Experimentelle Entwicklung",
            "Durchführbarkeitsstudie"
        ]
    )
    
    beschreibung = st.text_area(
        "Kurzbeschreibung (optional)",
        placeholder="Beschreiben Sie kurz das Projektziel..."
    )
    
    submit = st.form_submit_button("Projekt anlegen")

# Submit-Logik
if submit:
    if not projekt_name or not antragsteller:
        st.error("Bitte füllen Sie alle Pflichtfelder aus!")
    else:
        # Projekt erstellen
        projekt_id = create_projekt(
            projekt_name=projekt_name,
            antragsteller=antragsteller,
            modul=modul,
            projektart=projektart,
            beschreibung=beschreibung
        )
        
        st.success(f"✅ Projekt '{projekt_name}' erfolgreich angelegt!")
        st.session_state["current_projekt_id"] = projekt_id
        
        # Weiterleitung
        st.info("👉 Weiter zu Schritt 2: Dokumente hochladen")
```

### Backend-Logik

```python
# backend/projekt_manager.py

import uuid
from pathlib import Path
from datetime import datetime
import json

def create_projekt(
    projekt_name: str,
    antragsteller: str,
    modul: str,
    projektart: str,
    beschreibung: str = None
) -> str:
    """
    Erstellt neues Projekt im Dateisystem.
    
    Returns:
        projekt_id (str): Eindeutige ID des Projekts
    """
    
    # 1. Projekt-ID generieren
    projekt_id = f"projekt_{uuid.uuid4().hex[:8]}"
    
    # 2. Verzeichnisstruktur erstellen
    projekt_path = Path(f"data/projects/{projekt_id}")
    projekt_path.mkdir(parents=True, exist_ok=True)
    
    (projekt_path / "uploads").mkdir(exist_ok=True)
    (projekt_path / "extracted").mkdir(exist_ok=True)
    (projekt_path / "results").mkdir(exist_ok=True)
    
    # 3. Metadaten speichern
    metadata = {
        "projekt_id": projekt_id,
        "projekt_name": projekt_name,
        "antragsteller": antragsteller,
        "modul": modul,
        "projektart": projektart,
        "beschreibung": beschreibung,
        "status": "created",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat(),
        "documents": [],
        "checks_completed": {
            "parsing": False,
            "extraction": False,
            "foerdervoraussetzungen": False,
            "bewertung": False
        }
    }
    
    with open(projekt_path / "metadata.json", "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    return projekt_id
```

### Output
- Neues Verzeichnis: `data/projects/projekt_XXX/`
- Datei: `metadata.json`
- Session-State: `current_projekt_id` gesetzt

---

## SCHRITT 2: DOKUMENTE HOCHLADEN

### Ziel
Alle relevanten Projektdokumente hochladen und im System registrieren.

### UI-Elemente (Streamlit)

```python
# frontend/pages/2_Dokumente_hochladen.py

import streamlit as st
from pathlib import Path
import shutil

st.title("📄 Dokumente hochladen")

# Projekt laden
projekt_id = st.session_state.get("current_projekt_id")
if not projekt_id:
    st.error("Kein aktives Projekt! Bitte zuerst Projekt anlegen.")
    st.stop()

metadata = load_projekt_metadata(projekt_id)
st.info(f"Projekt: **{metadata['projekt_name']}** ({metadata['antragsteller']})")

# Dokumententypen definieren
DOC_TYPES = {
    "projektskizze": {"label": "📝 Projektskizze", "required": True, "formats": [".pdf", ".docx"]},
    "projektbeschreibung": {"label": "📋 Projektbeschreibung", "required": True, "formats": [".pdf", ".docx"]},
    "kalkulation": {"label": "💰 Projektkalkulation", "required": True, "formats": [".xlsx", ".xls"]},
    "kmu_erklaerung": {"label": "🏢 KMU-Erklärung", "required": True, "formats": [".pdf"]},
    "jahresabschluss_1": {"label": "📊 Jahresabschluss (Jahr -2)", "required": True, "formats": [".pdf"]},
    "jahresabschluss_2": {"label": "📊 Jahresabschluss (Jahr -1)", "required": True, "formats": [".pdf"]},
    "handelsregister": {"label": "📜 Handelsregisterauszug", "required": True, "formats": [".pdf"]},
    "finanzuebersicht": {"label": "💵 Finanz- und Arbeitsplatzübersicht", "required": True, "formats": [".xlsx", ".xls"]},
    "lebenslauf": {"label": "👤 Lebensläufe (optional)", "required": False, "formats": [".pdf"]},
    "loi": {"label": "📧 Letters of Intent (optional)", "required": False, "formats": [".pdf"]}
}

# Upload-Interface
uploaded_docs = {}

for doc_type, config in DOC_TYPES.items():
    st.subheader(config["label"])
    
    # Prüfen, ob bereits hochgeladen
    existing = next(
        (d for d in metadata["documents"] if d["doc_type"] == doc_type),
        None
    )
    
    if existing:
        st.success(f"✅ Bereits hochgeladen: {existing['filename']}")
        if st.button(f"🗑️ Löschen", key=f"delete_{doc_type}"):
            delete_document(projekt_id, doc_type)
            st.rerun()
    else:
        uploaded_file = st.file_uploader(
            f"Datei hochladen {config['formats']}",
            type=[fmt.replace(".", "") for fmt in config["formats"]],
            key=doc_type
        )
        
        if uploaded_file:
            uploaded_docs[doc_type] = uploaded_file

# Upload-Button
if st.button("📤 Alle Dateien hochladen", disabled=len(uploaded_docs) == 0):
    with st.spinner("Dateien werden hochgeladen..."):
        for doc_type, file in uploaded_docs.items():
            save_document(projekt_id, doc_type, file)
    
    st.success(f"✅ {len(uploaded_docs)} Dokument(e) hochgeladen!")
    st.rerun()

# Fortschrittsanzeige
total_required = sum(1 for cfg in DOC_TYPES.values() if cfg["required"])
uploaded_required = sum(
    1 for d in metadata["documents"]
    if DOC_TYPES.get(d["doc_type"], {}).get("required", False)
)

st.progress(uploaded_required / total_required)
st.write(f"**Fortschritt:** {uploaded_required}/{total_required} Pflichtdokumente hochgeladen")

# Weiter-Button
if uploaded_required >= total_required:
    if st.button("➡️ Weiter zu Schritt 3: Dokumente parsen"):
        st.switch_page("pages/3_Parsing.py")
else:
    st.warning(f"⚠️ Bitte laden Sie alle {total_required} Pflichtdokumente hoch.")
```

### Backend-Logik

```python
# backend/dokument_manager.py

def save_document(projekt_id: str, doc_type: str, uploaded_file) -> dict:
    """Speichert hochgeladenes Dokument."""
    
    # 1. Dateipfad generieren
    projekt_path = Path(f"data/projects/{projekt_id}")
    upload_path = projekt_path / "uploads"
    
    filename = f"{doc_type}_{uploaded_file.name}"
    file_path = upload_path / filename
    
    # 2. Datei speichern
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # 3. Metadaten aktualisieren
    metadata = load_projekt_metadata(projekt_id)
    
    doc_entry = {
        "doc_id": str(uuid.uuid4()),
        "doc_type": doc_type,
        "filename": filename,
        "original_filename": uploaded_file.name,
        "uploaded_at": datetime.now().isoformat(),
        "file_size": uploaded_file.size,
        "parsed": False
    }
    
    metadata["documents"].append(doc_entry)
    metadata["updated_at"] = datetime.now().isoformat()
    
    save_projekt_metadata(projekt_id, metadata)
    
    return doc_entry
```

### Output
- Dateien in `data/projects/projekt_XXX/uploads/`
- `metadata.json` aktualisiert mit Dokumentenliste

---

## SCHRITT 3: DOKUMENTE PARSEN

### Ziel
Alle hochgeladenen Dokumente parsen und Text/Daten extrahieren.

### UI-Elemente (Streamlit)

```python
# frontend/pages/3_Parsing.py

import streamlit as st

st.title("⚙️ Dokumente werden verarbeitet...")

projekt_id = st.session_state.get("current_projekt_id")
metadata = load_projekt_metadata(projekt_id)

# Parsing-Status
st.subheader("📄 Dokumente:")

progress_bar = st.progress(0)
status_text = st.empty()

parsed_count = 0
total_docs = len(metadata["documents"])

for i, doc in enumerate(metadata["documents"]):
    with st.expander(f"{doc['original_filename']}", expanded=True):
        
        if doc["parsed"]:
            st.success("✅ Bereits geparst")
        else:
            status_text.text(f"Parsing: {doc['original_filename']}...")
            
            try:
                # Parse-Funktion aufrufen
                parse_result = parse_document(projekt_id, doc["doc_type"])
                
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
