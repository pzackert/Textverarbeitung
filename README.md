# Masterprojekt: Vergleich von MVP und Plattform-Architektur

Dieses Repository dokumentiert die Entwicklung und Evolution eines RAG-basierten Systems zur Analyse von Ausschreibungsunterlagen. Es ist in drei Hauptbereiche unterteilt, die verschiedene Entwicklungsstadien und Architekturansätze repräsentieren.

## Struktur

### 📂 [option_1_mvp](./option_1_mvp/) – [README](./option_1_mvp/README.md)
**Der Initial-MVP (Legacy)**
- **Tech Stack:** Streamlit, Python, LM Studio (OpenAI Client).
- **Fokus:** Schnelle Validierung der RAG-Idee. Monolithische Struktur.
- **Status:** Eingefroren (Maintenance Mode).
- **Weitere Infos:** [Detailiertes README](./option_1_mvp/README.md)

### 📂 [option_2_platform](./option_2_platform/) – [README](./option_2_platform/README.md)
**Die Professionelle Plattform (Current)**
- **Tech Stack:** FastAPI, HTMX, TailwindCSS, Ollama, LangChain.
- **Architektur:** Modulare Service-Architektur, Dependency Injection, Asynchrone Verarbeitung.
- **Fokus:** Skalierbarkeit, UX, Wartbarkeit, Lokale LLM-Inferenz.
- **Status:** In aktiver Entwicklung.
- **Weitere Infos:** [Detailiertes README](./option_2_platform/README.md)

### 📂 [option_3_cloud](./option_3_cloud/) – [README](./option_3_cloud/README.md)
**Cloud-Native Vision (Future)**
- **Tech Stack:** Kubernetes, Microservices, Cloud-Provider APIs.
- **Fokus:** Horizontale Skalierung, Multi-Tenancy.
- **Status:** Geplant.
- **Weitere Infos:** [Detailiertes README](./option_3_cloud/README.md)

## Dokumentation
Die gesamte Projektdokumentation ist zentral im Ordner `docs/` konsolidiert.

- **[ARBEITSWEISE.md](docs/ARBEITSWEISE.md)** - Methodik & Best Practices (PFLICHTLEKTÜRE)
- **[INSTALLATION.md](docs/INSTALLATION.md)** - Setup & Installation (UV)
- **[USER_GUIDE.md](docs/USER_GUIDE.md)** - Benutzerhandbuch
- **[DEPLOYMENT.md](docs/DEPLOYMENT.md)** - Deployment Guide

Spezifische Anleitungen finden sich in den READMEs der jeweiligen Unterordner.

## Quick Start (Option 2)

Wir nutzen **UV** für das Package Management.

```bash
# 1. UV installieren
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Setup
cd option_2_platform
uv sync

# 3. Starten
uv run scripts/start_app.py
```
