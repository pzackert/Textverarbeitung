# Benutzerhandbuch (User Guide)

Willkommen beim IFB PROFI Dokumenten-Analyse-System. Dieses System hilft Ihnen, Informationen aus Förderrichtlinien und Anträgen schnell zu finden.

## Erste Schritte

1.  **System starten:**
    Bitten Sie Ihren Administrator, das System zu starten. Sie sollten Zugriff auf die Demo-Oberfläche (Terminal) haben.

2.  **Fragen stellen:**
    Geben Sie Ihre Frage einfach in natürlicher Sprache ein.
    
    *Beispiel:* "Wer ist für das PROFI Programm antragsberechtigt?"

## Funktionen

### 1. Fragen & Antworten
Das System sucht in allen gespeicherten Dokumenten nach der Antwort.
- **Antwort:** Eine zusammenfassende Erklärung.
## Web Interface

Das System verfügt nun über eine moderne Web-Oberfläche.

### 1. Dashboard
Hier sehen Sie den Status des Systems (Ollama, Datenbank) und eine Übersicht Ihrer Projekte.

### 2. Dokumente hochladen
1. Navigieren Sie zu einem Projekt.
2. Klicken Sie auf "Upload Document".
3. Wählen Sie eine PDF, DOCX oder XLSX Datei.
4. Das System verarbeitet die Datei automatisch und zeigt den Status an.

### 3. Chat Interface
Nutzen Sie den Chat, um Fragen zu Ihren Dokumenten zu stellen.
- Klicken Sie auf "Chat" in der Navigation.
- Geben Sie Ihre Frage ein.
- Das System antwortet basierend auf den hochgeladenen Dokumenten und zeigt Quellenangaben an.

### Fehlerbehebung
Sollte ein Fehler auftreten (z.B. "Ollama Offline"), wird dies im Dashboard und im Chat angezeigt. Bitte kontaktieren Sie den Administrator.
- **Liste der Dokumente:** Am Ende sehen Sie die genauen Dateinamen und Seitenzahlen.

### 2. Kriterien-Prüfung
Sie können prüfen, ob ein Antrag bestimmte Kriterien erfüllt.
*Frage:* "Erfüllt der Antragsteller die KMU-Kriterien?"

### 3. Zusammenfassungen
Sie können Dokumente zusammenfassen lassen.
*Frage:* "Fasse die Förderrichtlinie zusammen."

## Tipps für gute Ergebnisse

- **Seien Sie spezifisch:** Statt "Was ist mit Geld?", fragen Sie "Wie hoch ist die maximale Fördersumme?".
- **Kontext:** Nennen Sie das Programm, z.B. "Im PROFI Programm...".
- **Quellen prüfen:** Vertrauen Sie, aber prüfen Sie. Schauen Sie in die angegebenen Quellen (Seite X), um sicherzugehen.

## Häufige Fragen

**Q: Das System antwortet nicht.**
A: Prüfen Sie, ob der "Ollama" Dienst im Hintergrund läuft.

**Q: Die Antwort ist falsch.**
A: Das System basiert auf den Texten. Wenn der Text unklar ist, kann die Antwort ungenau sein. Prüfen Sie immer die Quelle.

**Q: Kann es Excel-Dateien lesen?**
A: Ja, sowie PDF und Word-Dokumente.
