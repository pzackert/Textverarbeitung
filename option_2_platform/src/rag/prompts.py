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
        
    def format(self, query: str, context: str, **kwargs) -> str:
        """Format complete prompt with query and context."""
        # In many LLM APIs (like OpenAI/Ollama), system prompt is passed separately.
        # However, for some models or simple completions, we might want to combine them.
        # Here we will return the user message formatted. The system prompt is stored
        # in the object to be retrieved by the LLM client if needed, or we can prepend it.
        # The requirement says "Format complete prompt", but usually chat models take messages.
        # Let's assume we return the formatted user content here, or a combined string if intended for completion.
        # Given the task description implies generating a prompt string, I will combine them if it's a single string return,
        # OR I will provide a method to get messages.
        # Looking at Task 1.2 interface: def format(...) -> str.
        # So I will return the full prompt string (System + User) or just User if System is handled elsewhere.
        # Let's prepend System Prompt for now to be safe for raw completion models, 
        # but usually for Chat models we separate them.
        # Let's stick to the interface and return a string.
        
        user_content = self.user_template.format(query=query, context=context, **kwargs)
        return f"{self.system_prompt}\n\n{user_content}"

    @classmethod
    def standard_query(cls) -> "PromptTemplate":
        """Create template for standard queries."""
        system_prompt = (
            "Du bist ein erfahrener Experte für IFB-Förderrichtlinien und das PROFI-Programm. "
            "Deine Aufgabe ist es, Fragen basierend auf den bereitgestellten Dokumenten präzise und professionell zu beantworten.\n"
            "Antworte immer auf Deutsch.\n"
            "Nutze ausschließlich die bereitgestellten Informationen aus dem Kontext.\n"
            "Wenn die Informationen im Kontext nicht ausreichen, sage dies offen. Erfinde keine Fakten.\n"
            "Zitiere deine Quellen, indem du die Nummer der Quelle in eckigen Klammern angibst (z.B. [Quelle 1])."
        )
        user_template = (
            "Kontext:\n"
            "{context}\n\n"
            "Frage:\n"
            "{query}\n\n"
            "Bitte beantworte die Frage basierend auf dem oben genannten Kontext. Gib die verwendeten Quellen an."
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

def format_context(results: List[Dict[str, Any]], include_scores: bool = False) -> str:
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
