# LLM Integration Specification

## 1. Provider Abstraction
Das System muss mehrere lokale LLM-Provider über ein einheitliches Interface `LLMClient` unterstützen.

### Supported Providers
1.  **Ollama** (Primär)
    - Protokoll: HTTP API (`http://localhost:11434/api/generate`)
    - Modelle: `qwen2.5:7b`, `qwen2.5:0.5b`
2.  **LM Studio** (Sekundär)
    - Protokoll: OpenAI-compatible API (`http://localhost:1234/v1`)
    - Modelle: Jedes geladene Modell

## 2. Model Konfiguration
Verwaltet in `config.yaml`:

```yaml
llm:
  provider: "ollama" # oder "lm_studio"
  model_name: "qwen2.5:7b"
  temperature: 0.1 # Niedrig für faktische Antworten
  max_tokens: 2048
  top_p: 0.9
  timeout: 60 # Sekunden
```

## 3. Prompt Engineering (Deutsch)
### System Prompt Template
```text
Du bist ein intelligenter Assistent für die IFB Hamburg (Investitions- und Förderbank).
Deine Aufgabe ist es, Fragen basierend auf den bereitgestellten Kontext-Dokumenten zu beantworten.

REGELN:
1. Antworte NUR basierend auf dem untenstehenden Kontext.
2. Wenn die Antwort nicht im Kontext steht, sage "Ich habe dazu keine Informationen in den Dokumenten gefunden."
3. Erfinde keine Fakten (Halluzination vermeiden).
4. Zitiere die Quelle (Dateiname), wenn möglich.
5. Antworte immer auf Deutsch.
6. Sei präzise und professionell (Banken-Standard).

KONTEXT:
{context}

FRAGE:
{question}
```

## 4. Response Parsing
- **Raw Text**: Extraktion des `response` Feldes aus JSON.
- **Citation Extraction**: (Optional) Parsen von "Quelle: ..." Referenzen.
- **Structured Output**: Für Criteria Engine (Phase 4) JSON-Modus erzwingen.

## 5. Error Handling
- **Connection Error**: 3 Retries mit exponentieller Backoff-Zeit.
- **Timeout**: Graceful Fail mit "LLM hat nicht rechtzeitig geantwortet."
- **Context Limit**: Truncation vor dem Senden (siehe Retrieval Strategy).

