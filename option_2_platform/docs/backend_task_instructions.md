# Backend Task Instructions (RAG & Chat Fixes)

## Kontext
Der User hat 10 Bugs gemeldet, wovon der Großteil Backend-Logik im Bereich RAG, Chat Context und Projekt-Isolation betrifft.
Ziel ist es, die technische Basis für korrekte Antworten, korrekte Quellenangaben und strikte Datentrennung zu schaffen.

## Zu bearbeitende Dateien (Primär)
- `src/rag/llm_chain.py` (Retrieval Logic, Prompt Construction)
- `src/api/routers/projects.py` (Chat Endpoint, Filter Logic)
- `src/api/routers/global_router.py` (oder wo der Global Chat liegt -> `src/api/routers/chats.py`?)
- `src/rag/ingestion.py` (Metadaten-Handling bei Ingest)
- `src/rag/vector_store.py` (Delete Logic Project Context)

## Aufgabenpakete

### 1. Fix: System Prompts & Begrüßung (Bug 3)
**Ziel:** Der Chat muss dynamisch die in `config.yaml` definierten Prompts laden.
- **Analyse:** Prüfe, wo `LLMChain` oder `ChatService` die Prompts initialisiert. Wahrscheinlich werden sie einmal beim Start geladen oder sind hardcodiert.
- **Action:**
    - Stelle sicher, dass `LLMChain` bei JEDEM Request (oder durch Reload-Logik) auf die `RAGConfig` zugreift.
    - Sende `prompts.global_chat_initial` als System Prompt an das LLM.
    - Sende `prompts.antwort_richtlinie` als Hidden Instruction vor jeder User-Query.

### 2. Fix: Projekt-Kontext Isolation (Bug 7, 8)
**Ziel:** Verhindern von Context Leaking zwischen Projekten.
- **Analyse:** Aktuell scheint der Filter `project_id` im Retrieval ignoriert zu werden oder die Chunks haben die Metadaten nicht.
- **Action:**
    - Prüfe `src/api/routers/projects.py`: Wird `metadata_filter={"project_id": project_id}` an `llm_chain.query()` übergeben? (Ja, Code sah so aus, bitte verifizieren).
    - Prüfe `src/rag/retrieval.py`: Wird der Filter tatsächlich an `vector_store.query()` durchgereicht?
    - **Cleanup:** Implementiere Logik für Bug 7 (Automatisches "Entladen" beim Verlassen). Da Chroma persistiert, bedeutet "Entladen" eigentlich nur "Filter korrekt setzen". Aber der User möchte "Rausladen".
    - **Alternative:** Implementiere `POST /projects/{id}/rag/unload` (löscht Vektoren aus Memory/Cache, falls vorhanden) oder versichere dem User, dass der Filter strikt ist.
    - **Test:** Schreibe einen Test, der Dokument A in Projekt A lädt, Dokument B in Projekt B, und sicherstellt, dass Query in A nicht B findet.

### 3. Fix: Quellenangaben & Phantom-Quellen (Bug 4, 5, 9)
**Ziel:** Korrekte Dateinamen und Reduktion halluzinierter Quellen.
- **Analyse:** "Dokument" statt Dateiname. Zu viele Quellen (top_k=10).
- **Action:**
    - **Benennung:** Stelle sicher, dass `doc_name` oder `filename` in den Metadaten des Chunks steht und im `ChatSource`-Objekt zurückgegeben wird. Ändere das Mapping in `src/api/routers/projects.py`.
    - **Filterung:** Implementiere `similarity_threshold` (z.B. 0.7) auch beim *Querying*. Verwerfe Chunks unterhalb des Schwellenwerts, bevor sie dem LLM gegeben oder als Quelle gelistet werden.
    - **Limit:** Reduziere ggf. `top_k` oder mache es dynamisch. Wenn alle Scores < X sind, gib "Keine Quellen" zurück.

### 4. Fix: RAG Qualität (Bug 1, 2)
**Ziel:** "Wer bist du?" muss beantwortet werden, wenn es im Kontext steht.
- **Action:**
    - Wenn Retrieval (Punkt 3) gefixt ist, sollte das bessere Context-Matching helfen.
    - Prüfe `embedding_model` Qualität für deutsche Anfragen.
    - Prüfe `chunk_overlap`. Ggf. erhöhen.

### 5. API für Frontend-Features (Bug 6, 10 Support)
**Ziel:** Backend muss Daten liefern, die das Frontend braucht.
- Spinner (Bug 10): API ist schon async/langsam, Frontend muss nur warten. (Kein Backend Change nötig).
- Quellen-Toggle (Bug 6): Frontend Sache. (Kein Backend Change nötig).

## Vorgehen
1.  **Context Fix (Priorität 1):** `project_id` Filterung in `project_service` und `llm_chain` härten.
2.  **Prompt Fix (Priorität 2):** Config-Prompts durchschleifen.
3.  **Source Fix (Priorität 3):** Metadaten durchreichen und Threshold-Filter einbauen.

**Output:** Funktionsfähiges Backend, das korrekt filtert und zitiert.
