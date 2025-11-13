# Projektübersicht: Automatisierte Antragsprüfung
## IFB PROFI System

**Version:** 2.0 (Architektur-Varianten)  
**Stand:** 10. November 2025

---

## 🎯 PROJEKT-ZIEL

Automatisierte Prüfung von Förderanträgen für das IFB PROFI-Programm mittels KI-gestützter Dokumentenanalyse.

**Kern-Features:**
- Automatische Dokumenten-Verarbeitung (PDF, DOCX, XLSX)
- RAG-basierte Informationsextraktion
- LLM-gestützte Kriterienprüfung (6 Förderkriterien)
- Streamlit Web-Interface
- 100% lokale Verarbeitung (Datenschutz)

---

## 🏗️ ARCHITEKTUR-VARIANTEN

Das System kann in drei Komplexitätsstufen implementiert werden:

### **Option 1: Super-Lite** (MVP - Empfohlen für Start)
- **Aufwand:** 5-7 Tage
- **LLM:** LM Studio (All-in-One)
- **RAG:** Minimales ChromaDB oder LM Studio Built-in
- **Ziel:** Schneller funktionsfähiger Prototyp

### **Option 2: Lite** (Production Single-User)
- **Aufwand:** 2-3 Wochen
- **LLM:** LM Studio (nur Inferenz)
- **RAG:** ChromaDB + LangChain
- **Ziel:** Produktionsreif mit mehr Kontrolle

### **Option 3: Full** (Enterprise)
- **Aufwand:** 2-3 Monate
- **LLM:** vLLM/TGI (Eigenes Hosting)
- **RAG:** Weaviate/Qdrant (Distributed)
- **Ziel:** Skalierbare Cloud-Lösung

**Empfehlung:** Start mit **Option 1**, dann Evaluation, ggf. Upgrade zu Option 2.

---

## 📑 DOKUMENTATIONSSTRUKTUR

### Allgemeine Dokumentation
- `PROJECT_OVERVIEW.md` - Diese Übersicht
- `TECHNICAL_ARCHITECTURE.md` - **WICHTIG: Architektur-Varianten im Detail**
- `SYSTEM_REQUIREMENTS.md` - Hardware/Software pro Variante
- `DEVELOPMENT_PRINCIPLES.md` - Entwicklungsprinzipien & Best Practices

### Prozesskomponenten (numbered)
1. `01_UI_FLOW.md` - UI-Design und Seitenfluss (Streamlit)
2. `02_DOCUMENT_PARSING.md` - Dokumenten-Parsing Framework (varianten-unabhängig)
3. `03_RAG_SYSTEM.md` - **RAG-Implementierung pro Variante**
4. `04_LLM_INTEGRATION.md` - **LLM-Setup pro Variante**
5. `05_CRITERIA_ENGINE.md` - Kriterienkatalog & Prüfmechanismus
6. `06_DATA_MANAGEMENT.md` - Datei- und Projektverwaltung
7. `07_BACKEND_CORE.md` - Backend-Architektur & Services
8. `08_SECURITY.md` - Sicherheitskonzept & Datenschutz

---

### Workflow
1. **Projekt anlegen**
   - Eindeutige Projekt-ID
   - Projektmetadaten erfassen
   - Backend-Ordner anlegen

2. **Dokumente hochladen**
   - Projektskizze (2-3 Seiten)
   - Projektantrag (Formular)

3. **Automatische Verarbeitung**
   - Dokumente parsen
   - RAG-Basis aufbauen (ChromaDB)
   - LLM-Integration aktivieren

4. **Kriterienprüfung**
   - 6 Kriterien sukzessive prüfen
   - Live-Status anzeigen
   - Ergebnisse speichern

5. **Ergebnisübersicht**
   - Erfüllte vs. nicht erfüllte Kriterien
   - Detaillierte Begründungen
   - Export-Funktionen

### Task-Generierung
- GitHub Copilot analysiert die Dokumentation
- Generiert konkrete Entwicklungsaufgaben
- Tasks werden in `/tasks` Ordner abgelegt
- Schrittweise Implementierung

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

