# Arbeitsweise & Best Practices - Projekt Textverarbeitung

## PYTHON ENVIRONMENT & PACKAGE MANAGEMENT

### UV Package Manager (PFLICHT)

**Das Projekt nutzt UV - NICHT pip oder venv!**

**Installation:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Projekt Setup:**
```bash
cd option_2_platform
uv sync  # Erstellt .venv/ und installiert Dependencies
```

**ALLE Python-Commands mit `uv run`:**
```bash
# ✅ RICHTIG:
uv run python script.py
uv run pytest
uv run scripts/start_app.py

# ❌ FALSCH:
python script.py
python3 script.py
source venv/bin/activate
pip install ...
```

**Warum UV:**
- ⚡ 10-100x schneller als pip
- 📦 Automatisches Environment Management
- 🔒 Reproduzierbare Builds (uv.lock)
- 🎯 Bessere Dependency Resolution

**Dependencies hinzufügen/entfernen:**
```bash
uv add package-name
uv remove package-name
uv sync  # Nach Änderungen an pyproject.toml
```

### Virtual Environment

- UV erstellt automatisch `.venv/` bei `uv sync`
- **NIEMALS manuell** `python -m venv` verwenden
- **NIEMALS** `pip` direkt verwenden
- `.venv/` ist in `.gitignore` (nicht committen)

### Dependencies-Management

**NUR essenzielle Dependencies in `pyproject.toml`:**
- Keine unnötigen Packages
- Keine veralteten Packages
- Regelmäßig bereinigen

**Vor jedem Commit:**
```bash
uv sync  # Dependencies synchronisieren
uv run pytest  # Tests durchlaufen
```

---

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
2. Dependencies installieren mit `uv sync`
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

---

## VERBOTENE AKTIONEN

❌ **NIEMALS:**
- `python -m venv venv`
- `source venv/bin/activate`
- `pip install ...` (ohne uv)
- `python3 script.py` (ohne uv run)
- Dependencies ohne Update von pyproject.toml
- Mehr als 50 Dependencies in pyproject.toml

✅ **IMMER:**
- `uv sync` nach Clone/Pull
- `uv run` für Python-Commands
- `uv add/remove` für Dependencies
- Arbeitsweise-Dokument lesen bei Unsicherheit
