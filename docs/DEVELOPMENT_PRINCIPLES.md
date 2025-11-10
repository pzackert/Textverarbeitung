# Entwicklungsprinzipien & Arbeitsweise
## IFB PROFI - Automatisierte Antragsprüfung

**Version:** 1.0  
**Stand:** 10. November 2025

## 🎯 Grundprinzipien

### KISS - Keep It Simple, Stupid
- **Einfachste Lösung zuerst** - Keine Überarchitektierung
- **Lokale Datenhaltung** - JSON-Files statt komplexe Datenbanken (außer für Vector Store)
- **Schritt für Schritt** - Kleine, nachvollziehbare Entwicklungsschritte
- **Selbstkontrolle** - Dreifache Überprüfung jedes Entwicklungsschritts

## 📊 Terminal-Output & Logging

### Grundsatz
**Jede Aktion muss im Terminal sichtbar sein!**

Das Terminal ist das primäre Monitoring-Tool während der Entwicklung und im Betrieb.

### Ausgabe beim Programmstart

```bash
$ streamlit run app.py

[SYSTEM] ================================
[SYSTEM] IFB PROFI - Antragsprüfung v1.0
[SYSTEM] ================================

[CONFIG] Lade Systemkonfiguration...
[CONFIG] ✓ config/system_config.json geladen
[CONFIG] ✓ config/criteria_catalog.json geladen

[LLM] Initialisiere LLM-Verbindung...
[LLM] ✓ LM Studio: localhost:1234
[LLM] ✓ Modell: mistral-7b-instruct-v0.2
[LLM] ✓ Context Window: 8192 tokens
[LLM] ✓ Cache: 1024 MB

[VECTORDB] Initialisiere ChromaDB...
[VECTORDB] ✓ Persist Directory: ./data/chromadb
[VECTORDB] ✓ Embedding Model: BAAI/bge-large-en-v1.5

[SYSTEM] ✓ System bereit!
[SYSTEM] UI verfügbar unter: http://localhost:8501
```

### Ausgabe bei fehlenden Komponenten

```bash
[CONFIG] Lade Systemkonfiguration...
[ERROR] ✗ config/system_config.json nicht gefunden!
[ERROR] → Erstelle Standard-Konfiguration...
[CONFIG] ✓ Standard-Konfiguration erstellt

[LLM] Initialisiere LLM-Verbindung...
[ERROR] ✗ LM Studio nicht erreichbar (localhost:1234)
[ERROR] → Prüfen Sie:
[ERROR]   1. Ist LM Studio gestartet?
[ERROR]   2. Läuft der Server auf Port 1234?
[ERROR]   3. Ist das Modell geladen?
[SYSTEM] ✗ System-Start abgebrochen - LLM nicht verfügbar
```

### Ausgabe während Dokumenten-Upload

```bash
[UPLOAD] Neues Dokument: projektskizze.pdf
[UPLOAD] ✓ Validierung: Format OK, Größe: 2.3 MB
[UPLOAD] ✓ Virus-Scan: Sauber
[UPLOAD] ✓ Gespeichert: /data/projects/proj_123/uploads/

[PARSING] Starte Dokumenten-Parsing...
[PARSING] → PDF: 5 Seiten erkannt
[PARSING] → Text-Extraktion... [█████████░] 90%
[PARSING] ✓ Text extrahiert: 3.450 Wörter
[PARSING] ✓ Gespeichert: /data/projects/proj_123/extracted/
```

### Ausgabe während RAG-Indexierung

```bash
[RAG] Starte Indexierung für Projekt: proj_123
[RAG] Dokumente: 2 (projektskizze.pdf, projektantrag.pdf)

[RAG] Chunking...
[RAG] → projektskizze.pdf: 12 Chunks erstellt
[RAG] → projektantrag.pdf: 18 Chunks erstellt
[RAG] ✓ Gesamt: 30 Chunks

[RAG] Erstelle Embeddings... [████████░░] 80%
[RAG] → Batch 1/3: 10 Chunks
[RAG] → Batch 2/3: 10 Chunks
[RAG] → Batch 3/3: 10 Chunks
[RAG] ✓ Embeddings erstellt

[CHROMADB] Speichere in Collection: projekt_proj_123
[CHROMADB] → 30 Vektoren gespeichert
[CHROMADB] ✓ Indexierung abgeschlossen (2.3s)
```

### Ausgabe während Kriterienprüfung

```bash
[CRITERIA] Starte Prüfung - 6 Kriterien
[CRITERIA] ================================

[K001] Projektort (1/6)
[K001] → RAG: Suche relevante Chunks...
[K001] → RAG: 5 Chunks gefunden (similarity: 0.92)
[K001] → LLM: Sende Prompt...
[K001] → LLM: Antwort erhalten (1.2s)
[K001] ✓ Erfüllt: Betriebsstätte Hamburg
[K001]   Quelle: projektantrag.pdf, Seite 2

[K002] Unternehmensalter (2/6)
[K002] → RAG: Suche relevante Chunks...
[K002] → RAG: 3 Chunks gefunden (similarity: 0.88)
[K002] → LLM: Sende Prompt...
[K002] → LLM: Antwort erhalten (0.9s)
[K002] ✓ Erfüllt: Gegründet 2020
[K002]   Quelle: handelsregister.pdf, Seite 1

[K003] Projektbeginn (3/6)
[K003] → RAG: Suche relevante Chunks...
[K003] → RAG: 4 Chunks gefunden (similarity: 0.85)
[K003] → LLM: Sende Prompt...
[K003] → LLM: Antwort erhalten (1.0s)
[K003] ✓ Erfüllt: Geplanter Start 01.01.2026
[K003]   Quelle: projektskizze.pdf, Seite 3

[K004] Projektziel (4/6)
[K004] → RAG: Suche relevante Chunks...
[K004] → RAG: 5 Chunks gefunden (similarity: 0.91)
[K004] → LLM: Sende Prompt...
[K004] → LLM: Antwort erhalten (1.5s)
[K004] ✓ Erfüllt: Neue Produktentwicklung
[K004]   Quelle: projektskizze.pdf, Seite 1-2

[K005] Finanzierung (5/6)
[K005] → RAG: Suche relevante Chunks...
[K005] → RAG: 4 Chunks gefunden (similarity: 0.89)
[K005] → LLM: Sende Prompt...
[K005] → LLM: Antwort erhalten (1.1s)
[K005] ✓ Erfüllt: 45.000 EUR (in Range 10k-100k)
[K005]   Quelle: projektkalkulation.pdf, Seite 1

[K006] Erfolgsaussicht (6/6)
[K006] → RAG: Suche relevante Chunks...
[K006] → RAG: 3 Chunks gefunden (similarity: 0.87)
[K006] → LLM: Sende Prompt...
[K006] → LLM: Antwort erhalten (1.3s)
[K006] ✓ Erfüllt: Ohne Förderung verzögert
[K006]   Quelle: projektskizze.pdf, Seite 3

[CRITERIA] ================================
[CRITERIA] ✓ Prüfung abgeschlossen (8.3s)
[CRITERIA] ✓ Ergebnis: 6/6 Kriterien erfüllt (100%)
[CRITERIA] → Gespeichert: /data/projects/proj_123/results/
```

## 🔧 Entwicklungs-Workflow

### Task-Prinzipien

1. **Kleinteilig**
   - Jeder Task max. 30 Min Entwicklungszeit
   - Ein Task = Eine klar definierte Funktionalität
   - Testbar und überprüfbar

2. **Selbstkontrolle (3x Check)**
   - Nach Implementation: Läuft der Code?
   - Nach Test: Funktioniert es wie erwartet?
   - Nach Review: Ist es die einfachste Lösung?

3. **Einfachheit First**
   - Wenn kompliziert → Schritt zurück
   - Gibt es einen einfacheren Weg?
   - Wenn festgefahren → Neuansatz mit einfacherem Ziel

### Task-Beispiel

#### ❌ Schlechter Task
```
"Implementiere komplettes Dokumenten-Parsing-System mit OCR, 
Tabellenerkennung und Multi-Format-Support"
```

#### ✅ Guter Task
```
Task 1: Implementiere PDF-Text-Extraktion
  - PyPDF2 verwenden
  - Nur Text, keine Bilder
  - Error-Handling
  - Test mit sample.pdf

Task 2: Speichere extrahierten Text als JSON
  - Format: {text, metadata}
  - Speicherort: /extracted/
  - Timestamp hinzufügen

Task 3: Erweitere um DOCX-Support
  - python-docx verwenden
  - Selber Output wie PDF
  - Test mit sample.docx
```

### Entwicklungs-Zyklus

```
1. Task lesen & verstehen
   ↓
2. Einfachste Lösung planen
   ↓
3. Implementieren
   ↓
4. CHECK #1: Code läuft?
   ↓
5. Testen
   ↓
6. CHECK #2: Funktioniert?
   ↓
7. Code-Review (selbst)
   ↓
8. CHECK #3: Einfachste Lösung?
   ↓
9. Commit & Nächster Task
```

### Bei Problemen

```python
# Wenn festgefahren nach 3 Versuchen:

if stuck_after_3_attempts:
    # 1. Problem analysieren
    print("[DEBUG] Was funktioniert nicht?")
    print("[DEBUG] Was ist die Fehlermeldung?")
    
    # 2. Vereinfachen
    print("[SOLUTION] Einfacheren Ansatz wählen:")
    print("  - Weniger Features")
    print("  - Bekanntere Library")
    print("  - Hardcoded statt dynamisch")
    
    # 3. Wenn immer noch stuck
    if still_stuck:
        print("[HELP] Frage um Hilfe!")
        ask_for_help()
```

## 📁 Datenhaltung

### Grundsatz
**Lokal, einfach, nachvollziehbar**

### Priorität
1. **JSON-Files** (Standard für Config, Metadaten, Ergebnisse)
2. **Filesystem** (Dokumente, Extrakte)
3. **ChromaDB** (nur für Vektoren - zwingend nötig)
4. **Keine SQL-DB** (erst wenn wirklich nötig!)

### Beispiel-Struktur
```
/data
  /projects
    /{projekt_id}
      metadata.json          # Projekt-Info
      /uploads
        projektskizze.pdf
      /extracted
        projektskizze.json   # Extrahierter Text
      /results
        criteria_2025_11_10.json  # Prüfergebnisse

/config
  system_config.json         # System-Config
  criteria_catalog.json      # Kriterienkatalog

/data/chromadb              # Vector Store
```

## 🤖 Copilot-Workflow

### Eigenständige Entwicklung
- Terminal-Kommandos selbst ausführen
- Tests selbst durchführen
- Fehler selbst debuggen
- Dreifach-Check durchführen

### Um Hilfe bitten wenn:
- 3 Versuche gescheitert
- Fundamentales Verständnisproblem
- Architektur-Entscheidung nötig
- Unsicher über Lösungsweg

### Code-Qualität
- **Einfach** > Clever
- **Lesbar** > Kurz
- **Funktional** > Perfekt
- **Getestet** > Angenommen

## 📝 Logging-Standards

### Log-Levels
```python
[SYSTEM]   # System-Start, -Stop, kritische Events
[CONFIG]   # Konfigurations-Laden/-Änderungen
[LLM]      # LLM-bezogene Operationen
[VECTORDB] # ChromaDB-Operationen
[RAG]      # RAG-Pipeline
[PARSING]  # Dokumenten-Parsing
[UPLOAD]   # Datei-Uploads
[CRITERIA] # Kriterienprüfung
[ERROR]    # Fehler
[DEBUG]    # Debug-Informationen (optional)
```

### Symbole
```
✓ - Erfolg
✗ - Fehler
→ - Aktion/Prozess
█ - Progress Bar
```

### Beispiel-Implementation
```python
import logging
from datetime import datetime

class TerminalLogger:
    """Einfacher Terminal-Logger"""
    
    @staticmethod
    def system(msg):
        print(f"[SYSTEM] {msg}")
    
    @staticmethod
    def success(category, msg):
        print(f"[{category}] ✓ {msg}")
    
    @staticmethod
    def error(category, msg):
        print(f"[{category}] ✗ {msg}")
    
    @staticmethod
    def process(category, msg):
        print(f"[{category}] → {msg}")
    
    @staticmethod
    def progress(category, current, total):
        pct = int((current / total) * 100)
        bar = "█" * (pct // 10) + "░" * (10 - pct // 10)
        print(f"[{category}] [{bar}] {pct}%")

# Verwendung
logger = TerminalLogger()
logger.system("IFB PROFI v1.0 gestartet")
logger.process("LLM", "Verbinde zu localhost:1234...")
logger.success("LLM", "Verbunden")
```

## ✅ Checkliste vor jedem Commit

- [ ] Code läuft ohne Fehler
- [ ] Terminal-Output ist informativ
- [ ] Dreifach-Check durchgeführt
- [ ] Einfachste Lösung gewählt
- [ ] Kommentare wo nötig
- [ ] Test durchgeführt
- [ ] Git-Commit-Message beschreibend
