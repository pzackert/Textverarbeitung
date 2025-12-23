import logging
import time
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel

from src.api.dependencies import get_llm_chain
from src.rag.llm_chain import LLMChain
from src.services.chat_store import load_or_create_project_chat, save_project_chat

router = APIRouter(prefix="/api/chats/project", tags=["chat_project"])
logger = logging.getLogger(__name__)

class ProjectMessageRequest(BaseModel):
    message: str
    include_rag: bool = True


def _build_metrics(answer: str, model: str, duration: float, stop_reason: str = "stop") -> Dict[str, Any]:
    total_tokens = len(answer.split()) if answer else 0
    total_time = max(duration, 0.001)
    ttfb = min(total_time, 0.1)
    return {
        "tokens_per_second": round(total_tokens / total_time, 4) if total_tokens else 0.0,
        "total_tokens": total_tokens,
        "time_to_first_token_sec": round(ttfb, 4),
        "stop_reason": stop_reason,
        "model": model,
        "total_generation_time_sec": round(total_time, 4),
    }


def _assistant_with_rag(message: str, project_id: str, llm_chain: LLMChain) -> Dict[str, Any]:
    started = time.perf_counter()
    result = llm_chain.query(
        question=message,
        metadata_filter={"project_id": project_id},
    )
    duration = result.get("metadata", {}).get("duration")
    if duration is None:
        duration = time.perf_counter() - started
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
    metrics = _build_metrics(result.get("answer", ""), llm_chain.config.llm_model, duration)
    return {
        "role": "assistant",
        "content": result.get("answer", ""),
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
    metrics = _build_metrics(answer, llm_chain.llm_provider.model_name, duration)
    return {
        "role": "assistant",
        "content": answer,
        "timestamp": None,
        "sources": [],
        "rag_used": False,
        "documents_used": [],
        "metrics": metrics,
    }


@router.get("/{project_id}")
async def get_or_create_chat(project_id: str):
    chat = load_or_create_project_chat(project_id)
    return chat


@router.post("/{project_id}/message")
async def send_project_message(project_id: str, request: ProjectMessageRequest, llm_chain: LLMChain = Depends(get_llm_chain)):
    chat = load_or_create_project_chat(project_id)
    now = datetime.utcnow().isoformat() + "Z"
    user_msg = {"role": "user", "content": request.message, "timestamp": now}
    if request.include_rag:
        assistant_msg = _assistant_with_rag(request.message, project_id, llm_chain)
    else:
        assistant_msg = _assistant_no_rag(request.message, llm_chain)

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
