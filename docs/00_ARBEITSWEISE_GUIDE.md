# Arbeitsweise & Best Practices - Projekt Textverarbeitung

## 1. GRUNDPRINZIPIEN DER ZUSAMMENARBEIT

### 1.1 Terminal-First Approach
- **Kernprinzip**: Alle Befehle werden direkt im Terminal ausgeführt, nicht im Chat beschrieben
- **Vorteil**: Echte Ausführung = sichere Funktionalität, keine Theorie
- **Implementierung**: Jeder Befehl mit `run_in_terminal` tool ausgeführt
- **Feedback**: Echte Terminal-Outputs zeigen sofort, ob etwas funktioniert
- **Vermeidung**: Keine Heredocs oder große Bash-Blöcke auf einmal

### 1.2 Inkrementelle Ausführung
- **Kleine Schritte**: Lieber 10 kleine Befehle als 1 großer Befehl
- **Grund**: Terminal-Verbindung bleibt stabil bei kleineren Operationen
- **Struktur**: Eine Aktion pro Terminal-Aufruf
- **Monitoring**: Nach jedem Schritt ist der Status klar

### 1.3 Klare Task-Struktur
- **Format**: Jede Task hat klare Inputs und Outputs
- **Tracking**: ✅ Task X.Y done - zeigt Fortschritt
- **Pausen**: Zwischen Phasen kurze Zusammenfassung
- **Validierung**: Jedes Ergebnis wird überprüft

---

## 2. TECHNISCHE WORKFLOWS

### 2.1 Code-Erstellung in Terminal
**NICHT diese Methode:**
```bash
cat > file.py << 'EOF'
# Großer Code-Block
EOF
```
**SONDERN diese Methode:**
- Python3-Inline-Skript nutzen
- `python3 << 'PYSCRIPT'` für Code-Erstellung
- Dateien mit Inhalt als String schreiben
- Danach mit `cat` verifizieren

**Vorteile:**
- Keine Heredoc-Probleme
- Code ist direkt testbar
- Terminal bleibt stabil

### 2.2 Datei-Operationen
**Strategie:**
1. Verzeichnisse erstellen: `mkdir -p path`
2. Dateien mit Python schreiben (nicht cat)
3. Inhalt mit `head` oder `cat` verifizieren
4. Git-Status überprüfen

**Beispiel-Flow:**
```bash
mkdir -p docs/
python3 << 'PYSCRIPT'
content = "..."
with open('docs/file.md', 'w') as f:
    f.write(content)
PYSCRIPT
cat docs/file.md | head -20
```

### 2.3 Test-Workflows
**Schritte:**
1. Unit-Tests schreiben (kleiner als Production-Code)
2. Dependencies installieren mit `uv pip install`
3. Tests mit `uv run pytest` ausführen
4. Outputs zeigen (verbose mode)
5. Real-World-Tests danach mit `uv run python3`

**Best Practice:**
- Tests IMMER mit echten Dateien validieren
- Mehrere Test-Cases pro Komponente
- Fail-Cases genauso wichtig wie Success-Cases

---

## 3. GIT & VERSIONSKONTROLLE

### 3.1 Branch-Strategie
- **Feature-Branches**: `feature/document-parser`, `feature/rag-system`
- **Granularität**: Ein großes Feature = ein Branch
- **Commits**: Nach abgeschlossener Funktionalität
- **Messages**: Aussagekräftig, mit Details

### 3.2 Commit-Praxis
**Gutes Format:**
```
feat: Implement document parsers (PDF, DOCX, XLSX)

- 3 parsers implemented with full metadata extraction
- 15 unit tests (5 per parser) - all passing
- 12 real files tested - 100% success rate
- Complete documentation provided
```

**Vorteile:**
- Klare Historie
- Rückverfolgbarkeit
- Andere können folgen

### 3.3 Push-Strategie
- Nach jedem größeren Checkpoint pushen
- Branches remote verfügbar machen
- Regelmäßiges Backup der Arbeit

---

## 4. DOKUMENTATION & SPEZIFIKATION

### 4.1 Spec-Kit Struktur
- **Ort**: `specs/02_document_parsing/`
- **Dateien**: 
  - `spec.md` - Gesamtübersicht
  - `metadata_schema.md` - Detaillierte Schemas
  - `tasks.md` - Aufgabenliste mit Status

### 4.2 Dokument-Typen
1. **Specification** (spec.md)
   - Overview
   - Implementation Order
   - Error Handling
   - Dependencies

2. **Schema Documentation** (metadata_schema.md)
   - Format-spezifische Felder
   - Datentypen
   - Beispiele

3. **Implementation Guides** (docs/*.md)
   - Usage Patterns
   - Code Examples
   - Best Practices
   - Findings & Lessons

4. **Status Reports** (logs/*.txt)
   - Test Results
   - Performance Analysis
   - Issues & Resolutions

### 4.3 Dokumentations-Workflow
- Specs VOR Implementation schreiben
- Code DANN entsprechend schreiben
- Tests SCHREIBEN um Spec zu validieren
- Findings NACH Implementation dokumentieren

---

## 5. ARCHITEKTUR-PATTERNS

### 5.1 Modulare Struktur
**Dieses Projekt nutzt:**
```
src/parsers/
├── __init__.py       # Public API
├── models.py         # Data structures
├── exceptions.py     # Error classes
├── base.py          # Abstract base
├── pdf_parser.py    # Concrete implementation
├── docx_parser.py   # Concrete implementation
└── xlsx_parser.py   # Concrete implementation
```

**Vorteile:**
- Clear separation of concerns
- Easy to test each module
- Simple to extend with new parsers

### 5.2 Abstraktionen
- **BaseParser**: Abstract class definiert Interface
- **Document**: Dataclass für standardisierte Ausgabe
- **Exceptions**: Custom exceptions für klares Error-Handling
- **Metadata**: Format-spezifische Schemas

### 5.3 Exportierung
`__init__.py` exportiert nur Public API:
```python
__all__ = [
    'Document',
    'BaseParser',
    'ParserError',
    'UnsupportedFormatError',
    'CorruptedFileError',
    'EmptyDocumentError'
]
```

---

## 6. TESTING-STRATEGIE

### 6.1 Unit-Tests (15 Tests)
**Pro Parser 5 Tests:**
1. Initialization
2. Accept correct format
3. Reject wrong formats
4. Handle missing files
5. Handle corrupted files

**Struktur:**
- Tests unter `tests/test_parsers/`
- Mit `uv run pytest` ausführbar
- Fixture-basiert für Parser-Instanzen
- Temp-Dateien für Edge-Cases

### 6.2 Integration-Tests (Real Files)
**12 Test-Dateien aus 4 Kategorien:**
- A_Perfekter Fall (Perfect Case)
- B_Mangelhafter Fall (Deficient Case)
- C_Umwelt-Kriterien (Environmental)
- D_Test (Complex Cases)

**Validierung:**
- 100% Success Rate erreicht
- Jeder Parser-Typ validiert
- Performance gemessen
- Keine Edge-Case-Fehler

### 6.3 Test-Reporting
- Quantitativ: X/Y tests passed
- Qualitativ: Findings & Observations
- Performance: Parse times
- Recommendations: Next steps

---

## 7. DEPENDENCY-MANAGEMENT

### 7.1 UV Package Manager
- **Installation**: `uv pip install <package>==<version>`
- **Versionskontrolle**: Exakte Versionen verwenden
- **Reproduzierbarkeit**: Gleiche Versionen = gleiche Ergebnisse

### 7.2 Verwendete Dependencies
```
pymupdf==1.26.6      # PDF parsing
python-docx==1.1.2   # DOCX parsing
openpyxl==3.1.5      # XLSX parsing
pytest==9.0.1        # Testing
```

### 7.3 Execution mit UV
- **Immer nutzen**: `uv run python3` statt `python3`
- **Grund**: Isolierte Environment, keine Konflikte
- **Tests**: `uv run pytest` für konsistente Test-Ausführung

---

## 8. FEHLER-HANDLING & DEBUGGING

### 8.1 Exception-Hierarchie
```
ParserError (base)
├── UnsupportedFormatError
├── CorruptedFileError
└── EmptyDocumentError
```

### 8.2 Debugging-Workflow
1. **Terminal-Output lesen**: Echte Fehlermeldung
2. **Kleine Tests schreiben**: Problem isolieren
3. **Schrittweise testen**: Komponente für Komponente
4. **Logs überprüfen**: `logs/` Verzeichnis für Details

### 8.3 Häufige Probleme & Lösungen
| Problem | Ursache | Lösung |
|---------|--------|--------|
| ModuleNotFoundError | Package nicht installiert | `uv pip install <package>` |
| Large heredoc fails | Terminal-Buffer überlädt | Kleinere Befehle nutzen |
| File permissions | Read-only Dateien | `chmod +x file` |
| Import errors | Pfad-Probleme | `uv run` verwenden |

---

## 9. ITERATIVER ENTWICKLUNGSPROZESS

### 9.1 Phase-Struktur
1. **Specification** (Was wollen wir?)
2. **Foundation** (Basis-Strukturen)
3. **Implementation** (Komponenten einzeln)
4. **Testing** (Unit + Integration)
5. **Documentation** (Findings)
6. **Finalization** (Commit + Push)

### 9.2 Checkpoint-System
- Nach jeder Phase: Zusammenfassung
- Status im Code: Tests passing/failing
- Git-History: Commits zeigen Fortschritt
- Docs: Aktuell halten mit Implementierung

### 9.3 Qualitäts-Metriken
- **Test Coverage**: 100% (15/15 tests passing)
- **Real File Coverage**: 100% (12/12 files parsed)
- **Code Quality**: Modular, maintainable
- **Documentation**: Complete

---

## 10. ZUSAMMENARBEIT MIT GIT & BRANCHES

### 10.1 Workflow
1. **Feature-Branch erstellen**: `git checkout -b feature/xxx`
2. **Lokal entwickeln**: Alle Arbeiten hier
3. **Commits machen**: Nach jedem Checkpoint
4. **Push**: `git push origin feature/xxx`
5. **Nächste Phase**: Neuer Branch von aktuellem Stand

### 10.2 Dieser Projekt-Verlauf
```
Hauptbranch (main)
├── feature/document-parser [COMPLETED]
│   ├── Specs erstellt
│   ├── 3 Parsers implementiert
│   ├── 15 Tests geschrieben & passed
│   ├── 12 Real-Files getestet
│   └── Committed & Pushed
│
└── feature/rag-system [STARTED]
    ├── Von document-parser branch
    ├── Nächste Phase beginnen
    └── ...
```

### 10.3 Verzweigungsstrategie
- **Feature-Isolierung**: Jedes Feature sein eigener Branch
- **Stabilität**: Main-Branch bleibt sauber
- **Parallelisierung**: Mehrere Features parallel möglich
- **Integration**: Nur fertige Features mergen

---

## 11. BEST PRACTICES ZUSAMMENGEFASST

### 11.1 DO's ✅
- ✅ Terminal-Befehle immer ausführen
- ✅ Kleine, fokussierte Tasks
- ✅ Nach jedem Schritt validieren
- ✅ Tests ZUERST schreiben (TDD-Ansatz)
- ✅ Real-World Daten testen
- ✅ Dokumentation mit Code synchron halten
- ✅ Dependencies mit exakten Versionen pinnen
- ✅ Commits aussagekräftig schreiben
- ✅ Regelmäßig pushen
- ✅ Logs & Reports generieren

### 11.2 DON'Ts ❌
- ❌ Große Befehle auf einmal
- ❌ Heredoc-Syntax für große Code-Blöcke
- ❌ Ohne Tests committen
- ❌ Ungetestete Real-World Files ignorieren
- ❌ Dependencies ohne Versionspins
- ❌ Docs veralten lassen
- ❌ Commits ohne aussagekräftige Messages
- ❌ Debugging nur im Chat (immer Terminal!)
- ❌ Branches nicht regelmäßig pushen
- ❌ Alte Branches nicht aufräumen

---

## 12. LESSONS LEARNED

### 12.1 Was Gut Funktioniert Hat
1. **Terminal-First**: Echte Ausführung = sichere Funktionalität
2. **Inkrementelle Tasks**: Kleine Schritte = stabile Verbindung
3. **Python für File-Ops**: Zuverlässiger als Bash-Heredocs
4. **Real-World Testing**: Validiert wirkliche Anforderungen
5. **Modulare Architektur**: Leicht zu verstehen & erweitern
6. **Spec-Kit Struktur**: Klare Vorgaben = bessere Implementierung

### 12.2 Herausforderungen & Lösungen
| Herausforderung | Lösung |
|-----------------|--------|
| Terminal-Crashes bei großen Befehlen | Kleine, geteilte Befehle |
| Heredoc-Syntax-Fehler | Python3 inline scripts |
| Verwirrte Ordnerstruktur | Klare hierarchische Struktur |
| Ungetestete Features | Unit + Real-World Tests |
| Veraltete Dokumentation | Docs mit Code updaten |

### 12.3 Skalierungsrichtlinien
- Für Phase 3+ gleiche Struktur verwenden
- Mehr Parsers? → Neuer Parser pro Datei
- Komplexere Tests? → Test-Utilities erstellen
- Größere Dateien? → Chunking-Strategie implementieren

---

## 13. NÄCHSTE PHASE (Phase 3: RAG System)

### 13.1 Aufbauend auf Phase 2
- Document-Model von Phase 2 nutzen
- Parser definieren die Input-Source
- RAG verarbeitet Document-Objekte

### 13.2 Struktur-Template
```
src/rag/
├── __init__.py
├── models.py        # RAG-spezifische Modelle
├── vector_store.py  # Chroma/Weaviate Integration
├── chunker.py       # Document chunking
└── retriever.py     # Query & Retrieval
```

### 13.3 Testing-Template
```
tests/test_rag/
├── test_vector_store.py
├── test_chunker.py
└── test_retriever.py
```

---

## 14. GLOSSAR & TERMINOLOGY

- **Task**: Atomare Arbeitseinheit (1.1, 2.3, etc.)
- **Phase**: Gruppierung mehrerer Tasks (Phase 1, 2, etc.)
- **Feature-Branch**: Git-Branch für ein großes Feature
- **Spec-Kit**: Dokumentation vor Implementation
- **Parser**: Code-Komponente die eine Datei in Document konvertiert
- **Document**: Standardisiertes Ausgabe-Format
- **Real-World Test**: Test mit echten Dateien (nicht Mock)
- **Unit Test**: Test einer einzelnen Komponente in Isolation

---

## 15. QUICK-START FÜR NÄCHSTE PHASES

**Schritte zum Starten einer neuen Phase:**

1. Neue Branch erstellen
   ```bash
   git checkout -b feature/next-feature
   ```

2. Spec-Kit erstellen (specs/03_xxx/)
   ```bash
   mkdir -p specs/03_xxx/
   # spec.md, schema.md erstellen
   ```

3. Foundation-Code schreiben
   ```bash
   mkdir -p src/xxx/
   # models.py, exceptions.py, base.py
   ```

4. Implementation + Tests
   ```bash
   # src/xxx/concrete_impl.py
   # tests/test_xxx/test_concrete.py
   ```

5. Real-World Validation
   ```bash
   uv run python3 << 'SCRIPT'
   # Test mit echten Dateien
   SCRIPT
   ```

6. Documentation & Commit
   ```bash
   # docs/XX_xxx_findings.md
   git add src/ tests/ specs/ docs/
   git commit -m "feat: Implement xxx"
   git push origin feature/next-feature
   ```

---

## FAZIT

Diese Arbeitsweise funktioniert optimal, weil sie:
- **Bewährte Praktiken** kombiniert (TDD, CI/CD thinking)
- **Real-World Validierung** als Kern hat
- **Klare Struktur** bietet (Specs → Code → Tests → Docs)
- **Modularität** maximiert (leicht zu erweitern)
- **Fehlervermeidung** durch Terminal-Ausführung
- **Nachverfolgbarkeit** durch Git-History
- **Skalierbarkeit** für größere Projekte

**Schlüssel zum Erfolg:**
Alles im Terminal ausführen, klein denken, oft validieren, dokumentieren.
