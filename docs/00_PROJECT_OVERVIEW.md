# Projektübersicht: Automatisierte Antragsprüfung
## IFB PROFI System

**Version:** 1.0  
**Stand:** 8. November 2025

## 📑 Dokumentationsstruktur

### Allgemeine Dokumentation
- `00_PROJECT_OVERVIEW.md` - Diese Übersicht
- `01_TECHNICAL_ARCHITECTURE.md` - Technische Architektur
- `SYSTEM_REQUIREMENTS.md` - Systemanforderungen

### Prozesskomponenten (numbered)
1. `01_UI_FLOW.md` - UI-Design und Seitenfluss
2. `02_DOCUMENT_PARSING.md` - Dokumenten-Parsing Framework
3. `03_RAG_SYSTEM.md` - RAG-Implementierung & ChromaDB
4. `04_LLM_INTEGRATION.md` - LLM-Modell Setup & Konfiguration
5. `05_CRITERIA_ENGINE.md` - Kriterienkatalog & Prüfmechanismus
6. `06_DATA_MANAGEMENT.md` - Datei- und Projektverwaltung
7. `07_BACKEND_CORE.md` - Backend-Architektur & Services
8. `08_SECURITY.md` - Sicherheitskonzept & Datenschutz

## 🔄 Entwicklungsprozess

1. **Dokumentationsphase**
   - Jede Komponente wird in einer eigenen Markdown-Datei detailliert beschrieben
   - Fokus auf klare Anforderungen und erwartetes Verhalten

2. **Task-Generierung**
   - GitHub Copilot analysiert die Dokumentation
   - Generiert konkrete Entwicklungsaufgaben
   - Tasks werden in GitHub Issues überführt

3. **Implementierung**
   - Schrittweise Umsetzung der Tasks
   - Kontinuierliche Integration in das Gesamtsystem

## 📊 Projektkomponenten

### 1. UI-Flow
- Benutzerführung
- Seitenaufbau
- Design-System
- Responsives Verhalten

### 2. Document-Parsing
- PDF-Verarbeitung
- Word/Excel-Integration
- Text-Extraktion
- Formatvalidierung

### 3. RAG-System
- ChromaDB Setup
- Indexierung
- Vektorisierung
- Retrieval-Logik

### 4. LLM-Integration
- Modell-Management
- Prompt-Engineering
- Inferenz-Pipeline
- Lokale Ausführung

### 5. Criteria-Engine
- Kriteriendefinition
- Prüflogik
- Bewertungsregeln
- Ergebnisvalidierung

### 6. Data-Management
- Projektverwaltung
- Dateisystem
- Metadaten-Handling
- Backup-Strategie

### 7. Backend-Core
- API-Design
- Service-Architektur
- Datenmodelle
- Fehlerbehandlung

### 8. Security
- Zugriffskontrollen
- Datenverschlüsselung
- Audit-Logging
- Compliance

## 🎯 Nächste Schritte

1. Review und Finalisierung der Dokumentationsstruktur
2. Detaillierte Ausarbeitung jeder Komponenten-Dokumentation
3. Task-Generierung durch GitHub Copilot
4. Priorisierung der Entwicklungsaufgaben
5. Start der Implementierung