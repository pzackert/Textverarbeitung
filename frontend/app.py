"""
Streamlit Frontend - Hauptseite
IFB PROFI - KI-gestützte Textverarbeitung
"""

import streamlit as st
from pathlib import Path

# Page Config
st.set_page_config(
    page_title="IFB PROFI - Textverarbeitung",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Hauptseite
st.title("📄 IFB PROFI - KI-gestützte Textverarbeitung")
st.markdown("---")

st.markdown("""
## Willkommen!

Diese Anwendung unterstützt Sie bei der automatisierten Prüfung von IFB PROFI Förderanträgen.

### 🚀 7-Schritte-Workflow

1. **Projekt anlegen** - Metadaten erfassen
2. **Dokumente hochladen** - PDF, DOCX, XLSX
3. **Dokumente parsen** - Text & Daten extrahieren
4. **Informationsextraktion** - RAG-basierte Analyse
5. **Fördervoraussetzungen prüfen** - Regelwerk anwenden
6. **Bewertung durchführen** - Scoring & Plausibilität
7. **Report & Checkliste generieren** - Markdown/PDF Export

### 📋 Nächste Schritte

Wählen Sie links im Menü **"1. Projekt anlegen"** um zu beginnen.
""")

# Sidebar
with st.sidebar:
    st.header("ℹ️ Informationen")
    st.info("""
    **Version:** 1.0  
    **Stand:** 31. Oktober 2025
    
    **Tech-Stack:**
    - LM Studio (Qwen 2.5)
    - LangChain + ChromaDB
    - Streamlit Frontend
    """)
    
    st.markdown("---")
    st.caption("© 2025 IFB PROFI Team")
