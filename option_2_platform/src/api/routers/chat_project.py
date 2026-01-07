import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.api.dependencies import get_llm_chain
from src.rag.llm_chain import LLMChain
from src.rag.config import RAGConfig
from src.services.chat_store import load_or_create_project_chat, save_project_chat
from src.api.dependencies import get_config

try:
    # optional import to inspect current RAG job status
    from src.api.routers import rag_project
except Exception:  # pragma: no cover
    rag_project = None

router = APIRouter(prefix="/chats/project", tags=["chat_project"])
logger = logging.getLogger(__name__)

class ProjectMessageRequest(BaseModel):
    message: str
    include_rag: bool = True


def _build_metrics(answer: str, model: str, duration: float, usage: Dict[str, Any] | None = None, stop_reason: str | None = None) -> Dict[str, Any]:
    usage = usage or {}
    completion_tokens = usage.get("completion_tokens") or usage.get("eval_count")
    prompt_tokens = usage.get("prompt_tokens") or usage.get("prompt_eval_count")
    total_tokens = completion_tokens if completion_tokens is not None else len(answer.split()) if answer else 0
    total_time = max(duration, 0.001)
    ttfb = usage.get("time_to_first_token_sec") or min(total_time, 0.1)
    stop = stop_reason or usage.get("finish_reason") or "stop"
    tokens_per_second = round(total_tokens / total_time, 4) if total_tokens else 0.0
    return {
        "tokens_per_second": tokens_per_second,
        "total_tokens": total_tokens,
        "prompt_tokens": prompt_tokens,
        "time_to_first_token_sec": round(ttfb, 4),
        "stop_reason": stop,
        "model": model,
        "total_generation_time_sec": round(total_time, 4),
    }


def _assistant_with_rag(message: str, project_id: str, llm_chain: LLMChain) -> Dict[str, Any]:
    started = time.perf_counter()
    prompts = RAGConfig.from_yaml().prompts
    # metadata_filter with include_global=True to allow current project + global knowledge
    # The RetrievalEngine handles the security logic (filtering out other projects)
    result = llm_chain.query(
        question=message,
        metadata_filter={"project_id": project_id, "include_global": True},
        system_prompt=getattr(prompts, "global_chat_initial", None),
        answer_guideline=getattr(prompts, "antwort_richtlinie", None),
    )
    meta = result.get("metadata", {}) or {}
    duration = meta.get("duration") or (time.perf_counter() - started)
    usage = getattr(getattr(llm_chain, "llm_provider", None), "last_usage", None)
    sources = result.get("sources", [])
    citations = result.get("citations", [])
    if not sources and citations:
        for cit in citations:
            if hasattr(cit, "source"):
                sources.append(cit.source.dict())
            elif isinstance(cit, dict):
                sources.append(cit)
    docs_used = []
    for s in sources:
        doc_name = s.get("document") or s.get("doc_name") or s.get("source")
        if doc_name:
            docs_used.append(doc_name)
    # Enforce sources for project chat (must cite uploads)
    # Relaxed Check: If no sources found, just return the LLM answer (which handles 'I don't know')
    # if not sources:
    #    raise HTTPException(status_code=503, detail="Projekt-RAG nicht geladen oder keine Quellen gefunden. Bitte RAG-Ingest starten.")
    metrics = _build_metrics(result.get("answer", ""), llm_chain.config.llm_model, duration, usage, meta.get("stop_reason"))
    answer_text = result.get("answer", "")
    if not answer_text:
        answer_text = "Entschuldigung, ich habe keine Antwort vom LLM erhalten. Bitte die LLM-Instanz prüfen."

    return {
        "role": "assistant",
        "content": answer_text,
        "timestamp": None,
        "sources": sources,
        "rag_used": True,
        "documents_used": docs_used,
        "metrics": metrics,
    }


def _assistant_no_rag(message: str, llm_chain: LLMChain) -> Dict[str, Any]:
    started = time.perf_counter()
    answer = "RAG ist deaktiviert. Bitte aktiviere RAG für projektspezifische Antworten."
    duration = time.perf_counter() - started
    usage = getattr(llm_chain.llm_provider, "last_usage", None)
    metrics = _build_metrics(answer, llm_chain.llm_provider.model_name, duration, usage)
    if not answer:
        answer = "Entschuldigung, ich habe keine Antwort vom LLM erhalten. Bitte die LLM-Instanz prüfen."
    return {
        "role": "assistant",
        "content": answer,
        "timestamp": None,
        "sources": [],
        "rag_used": False,
        "documents_used": [],
        "metrics": metrics,
    }


def _seed_handshake(chat: Dict[str, Any], prompts: Any) -> bool:
    if chat.get("messages"):
        return False
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    seeds = []
    if getattr(prompts, "global_chat_initial", None):
        seeds.append({"role": "system", "content": prompts.global_chat_initial, "timestamp": now})
    if getattr(prompts, "begruessung", None):
        seeds.append({"role": "assistant", "content": prompts.begruessung, "timestamp": now})
    if seeds:
        chat["messages"] = seeds
        chat["total_messages"] = len(seeds)
        chat["updated_at"] = now
        save_project_chat(chat)
        return True
    return False


@router.get("/{project_id}")
async def get_or_create_chat(project_id: str):
    chat = load_or_create_project_chat(project_id)
    # Handshake seeding if missing
    prompts = RAGConfig.from_yaml().prompts
    _seed_handshake(chat, prompts)
    return chat


@router.post("/{project_id}/message")
async def send_project_message(project_id: str, request: ProjectMessageRequest, llm_chain: LLMChain = Depends(get_llm_chain)):
    chat = load_or_create_project_chat(project_id)
    prompts = RAGConfig.from_yaml().prompts
    _seed_handshake(chat, prompts)
    # Optional: if there is an active ingestion job, block chat until ready
    if rag_project and hasattr(rag_project, "rag_jobs"):
        job = rag_project.rag_jobs.get(project_id)
        if job and job.get("status") not in {"ready", "unknown"}:
            # Soft check - just log/warn, don't crash
            logger.warning(f"Projekt-RAG noch im Status {job.get('status')} - Antwort könnte unvollständig sein.")
            # raise HTTPException(status_code=503, detail=f"Projekt-RAG Status: {job.get('status', 'unbekannt')}")
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    user_msg = {"role": "user", "content": request.message, "timestamp": now}
    try:
        if request.include_rag:
            assistant_msg = _assistant_with_rag(request.message, project_id, llm_chain)
        else:
            assistant_msg = _assistant_no_rag(request.message, llm_chain)
    except Exception as exc:
        logger.error(f"Project chat LLM failure for {project_id}: {exc}")
        raise HTTPException(status_code=503, detail="LLM nicht erreichbar oder Antwort fehlgeschlagen. Bitte Backend/LLM prüfen.")

    chat.setdefault("messages", []).extend([user_msg, assistant_msg])
    if not assistant_msg.get("timestamp"):
        assistant_msg["timestamp"] = now

    chat["updated_at"] = assistant_msg.get("timestamp") or user_msg["timestamp"]
    chat["total_messages"] = len(chat["messages"])
    save_project_chat(chat)

    return {
        "project_id": project_id,
        "message_id": f"msg_proj_{chat['total_messages']}",
        "user_message": user_msg,
        "assistant_message": assistant_msg,
        "saved_to": chat.get("file_path"),
    }
