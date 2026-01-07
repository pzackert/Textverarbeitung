from typing import List, Dict, Any, Optional

class PromptTemplate:
    """
    Prompt template system for RAG queries.
    Generates structured prompts with context and instructions.
    """
    
    def __init__(self, system_prompt: str, user_template: str):
        """Initialize with system prompt and user message template."""
        self.system_prompt = system_prompt
        self.user_template = user_template
        
    def format(self, query: str, context: str, system_prompt_override: Optional[str] = None, **kwargs) -> str:
        """Format complete prompt with query and context."""
        
        user_content = self.user_template.format(query=query, context=context, **kwargs)
        
        # Use override if provided, otherwise default
        sys_prompt = system_prompt_override if system_prompt_override else self.system_prompt
        
        return f"{sys_prompt}\n\n{user_content}"

    @classmethod
    def standard_query(cls) -> "PromptTemplate":
        """
        Create template for standard queries (Hybrid RAG).
        Allows general knowledge answers if context is insufficient.
        """
        system_prompt = (
            "Du bist ein erfahrener Experte der IFB Hamburg. "
            "Deine Aufgabe ist es, Fragen primär basierend auf den bereitgestellten Dokumenten zu beantworten.\n"
            "Antworte immer auf Deutsch.\n\n"
            "REGELN:\n"
            "1. Nutze ZUERST die Informationen aus dem Kontext.\n"
            "2. Wenn die Antwort im Kontext steht, zitiere die Quelle mit [Nummer] (z.B. [1]).\n"
            "3. Wenn die Frage NICHT aus dem Kontext beantwortet werden kann, aber allgemeines Wissen erfordert (z.B. Begrüßung, Mathe, Verständnisfragen), antworte aus deinem eigenen Wissen OHNE Zitate.\n"
            "4. Wenn du weder Kontext noch Wissen hast, sage offen, dass du keine Informationen finden konntest.\n"
            "5. Erfinde keine Fakten zu den Anträgen."
        )
        user_template = (
            "Kontext:\n"
            "{context}\n\n"
            "Frage:\n"
            "{query}\n\n"
            "Antwort:"
        )
        return cls(system_prompt, user_template)

    @classmethod
    def criteria_evaluation(cls) -> "PromptTemplate":
        """Create template for criteria evaluation."""
        system_prompt = (
            "Du bist ein spezialisierter Prüfer für Förderanträge der IFB Hamburg. "
            "Deine Aufgabe ist es, zu bewerten, ob spezifische Kriterien basierend auf den Dokumenten erfüllt sind.\n"
            "Antworte sachlich, objektiv und belege deine Aussagen mit Quellen aus dem Kontext."
        )
        user_template = (
            "Kontext:\n"
            "{context}\n\n"
            "Zu prüfendes Kriterium:\n"
            "{query}\n\n"
            "Bitte bewerte, ob das oben genannte Kriterium basierend auf dem Kontext erfüllt ist.\n"
            "Struktur der Antwort:\n"
            "- Bewertung: [Erfüllt / Nicht erfüllt / Teilweise erfüllt / Nicht beurteilbar]\n"
            "- Begründung: [Detaillierte Begründung mit Quellenangaben]\n"
            "- Relevante Textstellen: [Zitate aus dem Kontext]"
        )
        return cls(system_prompt, user_template)

    @classmethod
    def document_summary(cls) -> "PromptTemplate":
        """Create template for document summaries."""
        system_prompt = (
            "Du bist ein Assistent für Dokumentenanalyse im Bankenumfeld. "
            "Deine Aufgabe ist es, komplexe Dokumente prägnant und strukturiert zusammenzufassen."
        )
        user_template = (
            "Kontext:\n"
            "{context}\n\n"
            "Aufgabe:\n"
            "Bitte fasse die wichtigsten Punkte aus den bereitgestellten Dokumenten zusammen.\n"
            "Fokus:\n"
            "- Hauptziele und Zweck\n"
            "- Wichtige Anforderungen und Kriterien\n"
            "- Fristen, Termine und finanzielle Aspekte (falls vorhanden)\n"
            "- Wichtige Metadaten"
        )
        return cls(system_prompt, user_template)

def format_context(results: List[Dict[str, Any]], include_scores: bool = False, max_chars: int | None = None) -> str:
    """
    Format retrieval results into context string.
    
    Args:
        results: List of retrieved chunks with metadata
        include_scores: Whether to include relevance scores in the output
        
    Returns:
        Formatted context string with source markers
    """
    formatted_chunks = []
    for i, result in enumerate(results, 1):
        content = result.get("content", "").strip()
        if max_chars is not None and len(content) > max_chars:
            content = content[:max_chars] + "..."
        metadata = result.get("metadata", {})
        source = metadata.get("source", "Unbekannte Quelle")
        page = metadata.get("page", None)
        score = result.get("score", None)
        
        source_info = f"{source}"
        if page:
            source_info += f", Seite {page}"
        
        header = f"[Quelle {i}: {source_info}]"
        if include_scores and score is not None:
            header += f" (Relevanz: {score:.4f})"
            
        chunk_text = f"{header}\n{content}"
        formatted_chunks.append(chunk_text)
        
    return "\n\n".join(formatted_chunks)
