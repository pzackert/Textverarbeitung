import logging
import time
from datetime import datetime, timezone
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.api.dependencies import get_llm_chain
from src.rag.llm_chain import LLMChain
from src.rag.config import RAGConfig
from src.services.chat_store import (
    create_global_chat,
    list_global_chats,
    load_global_chat,
    save_global_chat,
    delete_global_chat,
)

router = APIRouter(prefix="/chats/global", tags=["chat_global"])
logger = logging.getLogger(__name__)

ISO_FMT = "%Y-%m-%dT%H:%M:%SZ"


class SendMessageRequest(BaseModel):
    message: str
    include_rag: bool = False


def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime(ISO_FMT)


def _build_metrics(answer: str, model: str, duration: float, usage: Dict[str, Any] | None = None, stop_reason: str | None = None) -> Dict[str, Any]:
    usage = usage or {}
    # Prefer provider token counts when available
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


def _seed_handshake(chat: Dict[str, Any], prompts: Any) -> None:
    if chat.get("messages"):
        return
    now = _utc_now()
    seeds = []
    if getattr(prompts, "global_chat_initial", None):
        seeds.append({"role": "system", "content": prompts.global_chat_initial, "timestamp": now})
    if getattr(prompts, "begruessung", None):
        seeds.append({"role": "assistant", "content": prompts.begruessung, "timestamp": now})
    if seeds:
        chat["messages"] = seeds
        chat["total_messages"] = len(seeds)
        chat["updated_at"] = now
        chat["last_message_preview"] = seeds[-1]["content"][:120]
        save_global_chat(chat)


def _assistant_with_rag(message: str, llm_chain: LLMChain, prompts: Any) -> Dict[str, Any]:
    started = time.perf_counter()
    result = llm_chain.query(
        question=message,
        metadata_filter={"include_global": True},
        system_prompt=getattr(prompts, "global_chat_initial", None),
        answer_guideline=getattr(prompts, "antwort_richtlinie", None),
    )
    meta = result.get("metadata", {}) or {}
    duration = meta.get("duration") or (time.perf_counter() - started)
    usage = getattr(getattr(llm_chain, "llm_provider", None), "last_usage", None)
    metrics = _build_metrics(result.get("answer", ""), llm_chain.config.llm_model, duration, usage, meta.get("stop_reason"))
    sources = result.get("sources") or result.get("citations") or []
    docs_used = []
    for src in sources:
        if isinstance(src, dict):
            doc_name = src.get("document") or src.get("doc_name") or src.get("source")
            if doc_name:
                docs_used.append(doc_name)
    answer_text = result.get("answer", "")
    if not answer_text:
        answer_text = "Entschuldigung, ich habe keine Antwort vom LLM erhalten. Bitte die LLM-Instanz prüfen."

    return {
        "role": "assistant",
        "content": answer_text,
        "timestamp": _utc_now(),
        "sources": sources,
        "rag_used": True,
        "documents_used": docs_used,
        "metrics": metrics,
    }


def _assistant_no_rag(message: str, llm_chain: LLMChain, prompts: Any) -> Dict[str, Any]:
    started = time.perf_counter()
    # Simple echo with safety note when RAG is disabled
    answer = "RAG ist deaktiviert. Bitte aktiviere RAG, um Wissensdatenbank-Antworten zu erhalten."
    try:
        answer = llm_chain.llm_provider.generate(
            prompt=message,
            max_tokens=llm_chain.config.llm_max_tokens,
            temperature=llm_chain.config.llm_temperature,
        )
    except Exception as exc:  # pragma: no cover - defensive fallback
        logger.warning(f"LLM plain generation failed: {exc}")
    duration = time.perf_counter() - started
    usage = getattr(llm_chain.llm_provider, "last_usage", None)
    metrics = _build_metrics(answer, getattr(llm_chain.llm_provider, "model_name", "unknown"), duration, usage)
    if not answer:
        answer = "Entschuldigung, ich habe keine Antwort vom LLM erhalten. Bitte die LLM-Instanz prüfen."
    return {
        "role": "assistant",
        "content": answer,
        "timestamp": _utc_now(),
        "sources": [],
        "rag_used": False,
        "documents_used": [],
        "metrics": metrics,
    }


def _add_preview(chat: Dict[str, Any]) -> Dict[str, Any]:
    preview = ""
    for msg in reversed(chat.get("messages", [])):
        if msg.get("role") in {"user", "assistant"}:
            preview = (msg.get("content") or "")[:120]
            break
    chat["last_message_preview"] = preview
    return chat


@router.get("/list")
async def list_chats():
    chats = [_add_preview(c) for c in list_global_chats()]
    return {"chats": chats}


@router.get("")
async def list_chats_root():
    return await list_chats()


@router.post("/create", status_code=201)
async def create_chat():
    chat = create_global_chat()
    prompts = RAGConfig.from_yaml().prompts
    _seed_handshake(chat, prompts)
    return chat


@router.get("/{chat_id}")
async def get_chat(chat_id: str):
    try:
        return load_global_chat(chat_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chat nicht gefunden")


@router.delete("/{chat_id}")
async def delete_chat(chat_id: str):
    try:
        delete_global_chat(chat_id)
        return {"status": "deleted", "chat_id": chat_id}
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chat nicht gefunden")


@router.post("/{chat_id}/message")
async def send_message(chat_id: str, request: SendMessageRequest, llm_chain: LLMChain = Depends(get_llm_chain)):
    try:
        chat = load_global_chat(chat_id)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Chat nicht gefunden")

    prompts = RAGConfig.from_yaml().prompts
    _seed_handshake(chat, prompts)

    now = _utc_now()
    user_msg = {"role": "user", "content": request.message, "timestamp": now}

    try:
        assistant_msg = (
            _assistant_with_rag(request.message, llm_chain, prompts)
            if request.include_rag
            else _assistant_no_rag(request.message, llm_chain)
        )
    except Exception as exc:
        logger.error(f"Global chat LLM failure: {exc}")
        raise HTTPException(status_code=503, detail="LLM nicht erreichbar oder Antwort fehlgeschlagen. Bitte Backend/LLM prüfen.")

    if not assistant_msg.get("timestamp"):
        assistant_msg["timestamp"] = _utc_now()

    chat.setdefault("messages", []).extend([user_msg, assistant_msg])
    chat["updated_at"] = assistant_msg["timestamp"]
    chat["total_messages"] = len(chat["messages"])
    _add_preview(chat)
    save_global_chat(chat)

    return {
        "chat_id": chat_id,
        "user_message": user_msg,
        "assistant_message": assistant_msg,
        "saved_to": chat.get("file_path"),
        "updated_at": chat.get("updated_at"),
    }
