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

- **[00_ARBEITSWEISE_GUIDE.md](docs/00_ARBEITSWEISE_GUIDE.md)** - Methodik & Best Practices
- **[INSTALLATION_MAC.md](docs/INSTALLATION_MAC.md)** - Installationsanleitung macOS
- **[INSTALLATION_WINDOWS.md](docs/INSTALLATION_WINDOWS.md)** - Installationsanleitung Windows
- **[10_PARSER_FINDINGS.md](docs/10_PARSER_FINDINGS.md)** - Erkenntnisse aus Phase 2 (Parser)
- **[11_PARSER_USAGE.md](docs/11_PARSER_USAGE.md)** - Nutzung der Parser
- **[12_TESTING_GUIDE.md](docs/12_TESTING_GUIDE.md)** - Testing Guide

Spezifische Anleitungen finden sich in den READMEs der jeweiligen Unterordner.

## Quick Start
Um mit der aktuellen Entwicklungsversion (Option 2) zu starten:
```bash
cd option_2_platform
# Siehe dortiges README.md
```
