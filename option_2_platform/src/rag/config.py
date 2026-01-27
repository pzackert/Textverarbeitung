from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from src.core.config import load_config


class ProviderSettings(BaseModel):
    models_dir: Optional[str] = None
    endpoint: Optional[str] = None


class LLMSettings(BaseModel):
    provider: str = "ollama"
    model: str = "qwen2.5:7b"
    temperature: float = 0.7
    max_tokens: int = 2000
    timeout: int = 120
    lm_studio: ProviderSettings = Field(default_factory=ProviderSettings)
    ollama: ProviderSettings = Field(default_factory=ProviderSettings)

    @property
    def base_url(self) -> str:
        if self.provider == "lm_studio" and self.lm_studio.endpoint:
            return self.lm_studio.endpoint
        if self.provider == "ollama" and self.ollama.endpoint:
            return self.ollama.endpoint
        # Fallback to LM Studio if provider set but endpoint missing
        if self.provider == "lm_studio" and self.ollama.endpoint:
            return self.ollama.endpoint
        return "http://127.0.0.1:11434"


class PromptsSettings(BaseModel):
    begruessung: str = "Hallo ich bin Herbert dein IFB Sacharbeiter Assistent. Wie kann ich dir helfen?"
    global_chat_initial: str = (
        "Du bist ein schlauer und genauer IFB Mitarbeiter Assistent. Deine Wissen basiert auf der Wissensdatenbank im RAG. "
        "Du prüfst gemeinsam mit anderen Sacharbeiter Anträge für die Vergabe von Förderbeträge"
    )
    antrags_chat_initial: str = (
        "Du liest alle Dokumente vom Antrag und analysierst genau was dieser Antrag soll. Du verstehst genau."
    )
    antwort_richtlinie: str = (
        "Deine Antworten sind kurz und knapp auf Deutsch und sehr präzise. Wenn du dich auf Quellen des Antrages beziehst, "
        "gibst du diese an. Wenn es mehrere Quellen gibt, kannst du mehrere angeben. Wenn du Antwort nicht weißt, dann trainiere nicht "
        "und gebe offen zu, dass du Sachen nicht weißt. Und gib ein Hinweis, wenn du nicht weiterkommst."
    )
    kriterien_pruefung: str = (
        "Lies das Kriterium, was zu prüfen ist, genau und gucke die Dokumente durch, ob du dieses Kriterium bestätigen oder ablehnen musst. "
        "Antworte in dem JSON Format."
    )


class RAGConfig(BaseModel):
    """Configuration model for the RAG system."""

    # RAG core
    chunk_size: int = 500
    chunk_overlap: int = 50
    embedding_model: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    top_k: int = 5
    similarity_threshold: float = 0.0
    persist_directory: str = "data/chromadb"
    collection_name: str = "ifb_documents"
    vector_store_path: str = "data/chromadb"
    metadata_schema_version: str = "docling-v1"
    default_template: str = "standard"
    include_scores: bool = False
    max_context_chunks: int = 5

    # Safety for oversized Docling blocks
    max_chunk_tokens: int = 800

    # New structured blocks
    llm: LLMSettings = Field(default_factory=LLMSettings)
    prompts: PromptsSettings = Field(default_factory=PromptsSettings)

    # Legacy compatibility fields (read-only, derived)
    llm_provider: str = "ollama"
    llm_model: str = "qwen2.5:7b"
    llm_base_url: str = "http://localhost:11434"
    llm_temperature: float = 0.7
    llm_max_tokens: int = 2000

    @classmethod
    def from_yaml(cls) -> "RAGConfig":
        """Load configuration from the central config.yaml file."""
        full = load_config()
        rag_data = full.get("rag", {})
        llm_data = full.get("llm", {})
        prompts_data = full.get("prompts", {})

        # Build nested settings
        llm_settings = LLMSettings(**llm_data) if llm_data else LLMSettings()
        prompts_settings = PromptsSettings(**prompts_data) if prompts_data else PromptsSettings()

        # Backfill legacy fields to keep current code working
        rag_data = dict(rag_data)
        rag_data.update({
            "llm": llm_settings,
            "prompts": prompts_settings,
            "llm_provider": llm_settings.provider,
            "llm_model": llm_settings.model,
            "llm_base_url": llm_settings.base_url,
            "llm_temperature": llm_settings.temperature,
            "llm_max_tokens": llm_settings.max_tokens,
        })

        return cls(**rag_data)

    @property
    def llm_timeout(self) -> int:
        return self.llm.timeout

    def to_dict(self) -> Dict[str, Any]:
        data = self.dict()
        return data
