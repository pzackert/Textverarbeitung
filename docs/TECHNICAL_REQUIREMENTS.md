# System & Technical Requirements

## System-Anforderungen

### Hardware
- **Minimum:** 8 GB RAM, 4 CPU Cores
- **Empfohlen:** 16 GB RAM, 8 CPU Cores
- **Storage:** 5 GB für Applikation + Modelle

### Software
- **Python:** 3.11+
- **UV:** Package Manager (für Dependency Management)
- **LM Studio:** Lokaler LLM Server oder alternativer OpenAI-kompatibler Server

## Technische Architektur

### Backend
- **Parser:** PyMuPDF, python-docx, openpyxl
- **RAG:** ChromaDB + sentence-transformers
- **LLM:** OpenAI-kompatible API (LM Studio, Ollama, etc.)
- **Config:** YAML-basierte Konfiguration

### Frontend
- **Framework:** Streamlit (webbasiert)
- **Design:** Responsiv, IFB-orientiert

### Datenhaltung
- **VectorDB:** ChromaDB (persistent)
- **Files:** Lokales Filesystem (data/input, data/projects)
- **Config:** config/config.yaml

## Sicherheit & Datenschutz
- **Lokal-First:** Alle Daten bleiben auf lokalem System oder privater Cloud
- **Keine externe API:** LLM läuft lokal (kein OpenAI, kein Cloud-Service)
- **Access Control:** Single-User System (MVP), Multi-User später

## Performance
- **Parsing:** < 5s für typisches Dokument (20 Seiten)
- **RAG Retrieval:** < 2s
- **LLM Response:** 5-30s (abhängig von Modell)
- **End-to-End:** < 60s für komplette Prüfung (6 Kriterien)
