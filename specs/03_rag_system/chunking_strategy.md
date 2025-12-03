# Chunking Strategy

## 1. Chunk Size & Overlap
- **Algorithm**: Recursive Character Text Splitter.
- **Chunk Size**: 500 Tokens (ca. 2000 Zeichen).
    - *Grund*: Groß genug für einen kompletten Absatz/Regelwerk, klein genug für mehrere Chunks im Kontext.
- **Overlap**: 50 Tokens (ca. 200 Zeichen).
    - *Grund*: Verhindert Kontextverlust an Schnittstellen.

## 2. Boundary Handling
Der Splitter respektiert folgende Hierarchie:
1.  `\n\n` (Absätze)
2.  `\n` (Zeilen)
3.  `. ` (Sätze)
4.  ` ` (Wörter)
5.  `` (Zeichen)

## 3. Special Content Handling
- **Tabellen**: Werden idealerweise zusammengehalten. Wenn größer als Chunk-Size, wird gesplittet (Header-Wiederholung als Future Feature).
- **Listen**: Listenelemente werden mit ihrem Einleitungssatz zusammengehalten.

## 4. Metadata Preservation
Jeder Chunk erbt Metadaten vom Elterndokument:
- `source`: Dateiname
- `page`: Seitennummer (kritisch für Zitate)
- `doc_type`: Dateityp
- `chunk_id`: Sequentielle ID im Dokument

## 5. Quality Metrics
- **Kohärenz**: Ergibt der Chunk alleine Sinn?
- **Vollständigkeit**: Wird ein Satz mitten drin abgeschnitten?
- **Validierung**: Stichprobenartige Prüfung der Lesbarkeit.

## 6. Deutsche Sprache
- **Besonderheiten**: Lange Komposita (z.B. "Investitionsförderungsrichtlinie").
- **Handling**: Tokenizer muss mit deutschen Wortstrukturen umgehen können.
- **Umlaute**: Korrektes Encoding (UTF-8) sicherstellen.

