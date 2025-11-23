from __future__ import annotations

import logging

import pandas as pd
import streamlit as st

st.set_page_config(page_title="Technische Lösungen", layout="wide")

LOGGER = logging.getLogger("frontend.app")
if not LOGGER.handlers:
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    LOGGER.addHandler(handler)
LOGGER.setLevel(logging.INFO)
LOGGER.info("page_view | {'page': 'technische_loesungen'}")

st.header("💡 Technische Lösungsoptionen")
st.subheader("Vergleich der drei Implementierungsansätze für das IFB PROFI System")
st.write("Von der schnellen MVP-Lösung bis zur skalierbare Cloud-Architektur - hier finden Sie alle technischen Optionen im Überblick.")

OPTIONS = ["Option 1: LM Studio Lightweight", "Option 2: Custom RAG System", "Option 3: Cloud-basiert Professional"]


def _render_table(df: pd.DataFrame, caption: str | None = None) -> None:
    """Render tables with consistent column widths for readability."""
    column_config = {col: st.column_config.TextColumn(width="medium") for col in df.columns}
    st.dataframe(df, use_container_width=True, column_config=column_config, hide_index=False)
    if caption:
        st.caption(caption)

st.markdown("## Technische Lösungsoptionen - Tabellarische Übersicht")
st.caption("📊 Vergleichsmatrix für IFB PROFI System")
overview_df = pd.DataFrame(
    {
        "Kriterium": ["Status", "Beschreibung"],
        OPTIONS[0]: ["✅ Aktuell implementiert (MVP)", "LM Studio Backend · Streamlit Frontend"],
        OPTIONS[1]: ["🔧 Masterprojekt-Ziel", "Custom RAG Plattform mit erweitertem Funktionsumfang"],
        OPTIONS[2]: ["🚀 Zukunftsoption", "Enterprise Cloud Lösung mit unbegrenzter Skalierung"],
    }
)
_render_table(overview_df.set_index("Kriterium"))

st.markdown("### 🖥️ Hardware-Anforderungen")
hardware_df = pd.DataFrame(
    {
        "Komponente": ["GPU", "GPU-Speicher", "RAM", "CPU", "Speicher", "Hosting"],
        OPTIONS[0]: [
            "NVIDIA RTX 3060 (12GB) / Apple M1/M2",
            "10-16 GB VRAM",
            "16 GB",
            "Mittelklasse (i5/i7, Ryzen 5/7)",
            "100 GB SSD",
            "Lokaler Rechner/Workstation",
        ],
        OPTIONS[1]: [
            "NVIDIA RTX 4090 (24GB) / A6000 (48GB)",
            "24-48 GB VRAM",
            "32-64 GB",
            "High-End (i9, Ryzen 9, Threadripper)",
            "500 GB - 1 TB NVMe",
            "Dedizierter Server/Workstation",
        ],
        OPTIONS[2]: [
            "Cloud GPU (A100 80GB, H100)",
            "40-80 GB VRAM (skalierbar)",
            "64-128 GB (skalierbar)",
            "Cloud vCPUs (16-32 Cores)",
            "Cloud Storage (flexibel)",
            "AWS / Azure / GCP",
        ],
    }
)
_render_table(hardware_df.set_index("Komponente"))

st.markdown("### ⚙️ Technische Architektur")
architecture_df = pd.DataFrame(
    {
        "Komponente": ["LLM Backend", "Modelle", "RAG System", "Dokument-Parser", "Vector DB", "Frontend", "API"],
        OPTIONS[0]: [
            "LM Studio (lokal)",
            "Qwen 2.5 (3-7B)",
            "LM Studio integriert",
            "LM Studio Basic",
            "LM Studio intern",
            "Streamlit",
            "LM Studio REST API",
        ],
        OPTIONS[1]: [
            "Custom Python Backend (Ollama/llama.cpp)",
            "Qwen 2.5, Llama 3.1 (8-70B)",
            "Custom ChromaDB + LangChain",
            "PyMuPDF, Unstructured, Custom Parser",
            "ChromaDB (lokal)",
            "FastAPI + HTMX + Tailwind",
            "Custom FastAPI",
        ],
        OPTIONS[2]: [
            "OpenAI / Anthropic / Azure OpenAI",
            "GPT-4, Claude 3.5, Gemini (175B+)",
            "Pinecone / Weaviate (Enterprise)",
            "Adobe PDF Services, AWS Textract",
            "Pinecone, Qdrant, Weaviate (Cloud)",
            "React / Next.js + shadcn/ui",
            "RESTful + GraphQL",
        ],
    }
)
_render_table(architecture_df.set_index("Komponente"))

st.markdown("### 🎯 Funktionen & Capabilities")
functions_df = pd.DataFrame(
    {
        "Funktion": [
            "Dokument-Formate",
            "RAG-Qualität",
            "Chunking",
            "Embedding-Modelle",
            "Batch-Verarbeitung",
            "Multi-User",
            "Monitoring",
            "Fehlerbehandlung",
        ],
        OPTIONS[0]: [
            "PDF, DOCX, TXT (Basic)",
            "Standard",
            "Basic (feste Größe)",
            "all-MiniLM",
            "Begrenzt",
            "Nein",
            "Terminal-Logs",
            "Basic",
        ],
        OPTIONS[1]: [
            "PDF, DOCX, XLSX, TXT, HTML (Advanced)",
            "Sehr gut",
            "Semantisch intelligent",
            "multilingual-e5, BGE",
            "Ja (Multi-Threading)",
            "Ja (Session-Management)",
            "Prometheus + Grafana",
            "Erweitert mit Retry-Logic",
        ],
        OPTIONS[2]: [
            "Alle Formate + OCR + Scans",
            "Exzellent",
            "KI-gestützt mit Kontext",
            "OpenAI ada-002, Cohere",
            "Ja (hochskalierbar)",
            "Ja (Enterprise-Authentication)",
            "CloudWatch, DataDog",
            "Enterprise-Grade",
        ],
    }
)
_render_table(functions_df.set_index("Funktion"))

st.markdown("### 💰 Kosten & Aufwand")
cost_df = pd.DataFrame(
    {
        "Kostenart": [
            "Hardware (einmalig)",
            "Software-Lizenzen",
            "Monatliche Kosten",
            "API-Kosten pro 1M Token",
            "Entwicklungszeit",
            "Wartungsaufwand",
        ],
        OPTIONS[0]: [
            "1.500 - 2.500 €",
            "0 € (Open Source)",
            "~30 € (Strom)",
            "0 €",
            "2-4 Wochen (fertig)",
            "Niedrig",
        ],
        OPTIONS[1]: [
            "3.000 - 8.000 €",
            "0 € (Open Source)",
            "~50-100 € (Strom/Wartung)",
            "0 €",
            "3-4 Monate",
            "Mittel",
        ],
        OPTIONS[2]: [
            "0 € (Cloud)",
            "Variable (API-Kosten)",
            "500 - 2.000 €",
            "5-30 €",
            "6-12 Monate",
            "Niedrig (Managed)",
        ],
    }
)
_render_table(cost_df.set_index("Kostenart"))

st.markdown("### ✅ Vorteile")
advantages_df = pd.DataFrame(
    {
        "Aspekt": [
            "Datenschutz",
            "Einstiegshürde",
            "Time-to-Market",
            "Kosten",
            "Flexibilität",
            "Performance",
            "Anpassbarkeit",
        ],
        OPTIONS[0]: [
            "✅ 100% lokal",
            "✅ Sehr niedrig",
            "✅ Sofort einsatzbereit",
            "✅ Sehr günstig",
            "⚠️ Begrenzt durch LM Studio",
            "⚠️ Gut für 3-7B Modelle",
            "❌ Begrenzt",
        ],
        OPTIONS[1]: [
            "✅ 100% lokal",
            "⚠️ Mittel",
            "⚠️ 3-4 Monate",
            "✅ Mittlere Investition",
            "✅ Vollständig anpassbar",
            "✅ Sehr gut für 8-70B",
            "✅ Custom",
        ],
        OPTIONS[2]: [
            "⚠️ Cloud-abhängig",
            "⚠️ Cloud-Setup",
            "⚠️ 6+ Monate",
            "❌ Hohe laufende Kosten",
            "✅ Hoch skalierbar",
            "✅ Exzellent",
            "✅ API-basiert erweiterbar",
        ],
    }
)
_render_table(advantages_df.set_index("Aspekt"))

st.markdown("### ❌ Nachteile")
disadvantages_df = pd.DataFrame(
    {
        "Aspekt": [
            "Skalierbarkeit",
            "Modell-Größe",
            "Dokument-Parsing",
            "Multi-User",
            "UI/UX",
            "Wartung",
            "Vendor Lock-in",
        ],
        OPTIONS[0]: [
            "❌ Begrenzt auf einen Rechner",
            "❌ Max. 7B realistisch",
            "❌ Basic",
            "❌ Single-User",
            "❌ Streamlit-Limitierungen",
            "✅ Minimal",
            "✅ Kein Lock-in",
        ],
        OPTIONS[1]: [
            "⚠️ Horizontal skalierbar (Aufwand)",
            "⚠️ Max. 70B",
            "✅ Erweitert",
            "✅ Möglich",
            "✅ Modern",
            "⚠️ Mittel",
            "✅ Kein Lock-in",
        ],
        OPTIONS[2]: [
            "✅ Automatisch skalierbar",
            "✅ Unbegrenzt",
            "✅ Enterprise-Level",
            "✅ Native Unterstützung",
            "✅ State-of-the-art",
            "✅ Managed",
            "⚠️ Cloud-Abhängigkeit",
        ],
    }
)
_render_table(disadvantages_df.set_index("Aspekt"))

st.markdown("### 📈 Performance & Qualität")
performance_df = pd.DataFrame(
    {
        "Metrik": ["Antwortzeit", "Tokens/Sekunde", "RAG-Accuracy", "Dokument-Verarbeitung", "Gleichzeitige Nutzer"],
        OPTIONS[0]: ["5-15 s (3B)", "20-40", "70-80%", "1-2 Dokumente parallel", "1-5"],
        OPTIONS[1]: ["10-30 s (13B)", "40-80", "80-90%", "5-10 Dokumente parallel", "5-10"],
        OPTIONS[2]: ["2-5 s", "100-200", "90-95%", "Unbegrenzt", "100+"],
    }
)
_render_table(performance_df.set_index("Metrik"))

st.markdown("### 🔧 Entwicklungsaufwand")
effort_df = pd.DataFrame(
    {
        "Phase": ["Setup", "Entwicklung", "Testing", "Deployment", "Dokumentation"],
        OPTIONS[0]: ["1 Tag", "2-4 Wochen (fertig)", "1 Woche", "Lokal (sofort)", "Basic"],
        OPTIONS[1]: ["1-2 Wochen", "3-4 Monate", "2-4 Wochen", "On-Premise (1 Woche)", "Umfassend"],
        OPTIONS[2]: ["1-2 Wochen", "6-12 Monate", "4-8 Wochen", "Cloud (2-4 Wochen)", "Enterprise-Level"],
    }
)
_render_table(effort_df.set_index("Phase"))

st.divider()
with st.container():
    st.header("🧭 Bewertung & Empfehlung")
    st.write(
        "Option 1 bleibt das produktionsreife MVP, Option 2 ist das konkrete Masterprojekt-Ziel und Option 3 bildet die skalierbare Roadmap nach erfolgreichem Projektabschluss."
    )
    rating_cols = st.columns(3)
    with rating_cols[0]:
        st.metric("Option 1", "Score: 7/10", "Sofort nutzbar")
        st.success("Ideal für Demo & lokale Einsätze")
    with rating_cols[1]:
        st.metric("Option 2", "Score: 8/10", "Masterprojekt")
        st.info("Beste Balance aus Kontrolle, Funktionsumfang und Datenschutz")
    with rating_cols[2]:
        st.metric("Option 3", "Score: 6/10", "Roadmap")
        st.warning("Hoher Aufwand, lohnt für Enterprise-Szenarien")

st.divider()
with st.container():
    st.header("🎓 Fahrplan")
    st.info(
        """
        Phase 1 (Aktuell): Option 1 - MVP Demo (standalone, lokal und einsatzbereit)

        Phase 2 (Masterprojekt): Option 2 - Custom Development (RAG-Platform mit erweiterten Modellen)

        Phase 3 (Nach Projekt): Option 3 - Cloud Migration (Enterprise-Scale, Managed Services)
        """
    )