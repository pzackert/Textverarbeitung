import os
import logging
from pathlib import Path
from typing import Dict, Any, List
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from pydantic import BaseModel, Field

from src.core.config import load_config, save_config, invalidate_config_cache
from src.rag.config import RAGConfig
from src.services.model_scanner import scan_all_models
from src.api.dependencies import get_ingestion_pipeline
from src.services.knowledge_service import knowledge_service, GLOBAL_KNOWLEDGE_DIR
from src.rag.vector_store import VectorStore

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/settings", tags=["settings"])


class LLMUpdate(BaseModel):
    provider: str | None = Field(default=None)
    model: str
    temperature: float
    max_tokens: int
    timeout: int


class RAGUpdate(BaseModel):
    chunk_size: int
    chunk_overlap: int
    top_k: int


class PromptsUpdate(BaseModel):
    begruessung: str
    global_chat_initial: str
    antrags_chat_initial: str
    antwort_richtlinie: str
    kriterien_pruefung: str


def _load_fresh_config() -> Dict[str, Any]:
    return load_config(force_reload=True)


def _save_and_refresh(data: Dict[str, Any]):
    save_config(data)
    invalidate_config_cache()


def _disk_usage_mb(path: str) -> float:
    total = 0
    root = Path(path)
    if not root.exists():
        return 0.0
    for p in root.rglob("*"):
        if p.is_file():
            total += p.stat().st_size
    return round(total / (1024 * 1024), 2)


@router.get("")
async def get_settings():
    cfg = _load_fresh_config()
    rag_cfg = RAGConfig.from_yaml()
    models = scan_all_models(rag_cfg.llm)
    cfg["available_models"] = models
    return cfg


@router.get("/models")
async def list_models():
    rag_cfg = RAGConfig.from_yaml()
    return {"models": scan_all_models(rag_cfg.llm)}


@router.post("/llm")
async def update_llm(settings: LLMUpdate):
    cfg = _load_fresh_config()
    llm = cfg.get("llm", {})
    if settings.provider:
        llm["provider"] = settings.provider
    llm["model"] = settings.model
    logger.info(f"Updating LLM Config: {llm}")
    llm["temperature"] = settings.temperature
    llm["max_tokens"] = settings.max_tokens
    llm["timeout"] = settings.timeout
    cfg["llm"] = llm
    _save_and_refresh(cfg)
    return {"status": "ok", "restart_required": True}


@router.post("/rag")
async def update_rag(settings: RAGUpdate):
    cfg = _load_fresh_config()
    rag = cfg.get("rag", {})
    rag["chunk_size"] = settings.chunk_size
    rag["chunk_overlap"] = settings.chunk_overlap
    rag["top_k"] = settings.top_k
    cfg["rag"] = rag
    _save_and_refresh(cfg)
    return {"status": "ok", "restart_required": True}


@router.post("/prompts")
async def update_prompts(settings: PromptsUpdate):
    cfg = _load_fresh_config()
    prompts = cfg.get("prompts", {})
    prompts.update(settings.dict())
    logger.info(f"Updating Prompts: {settings.dict().keys()}")
    cfg["prompts"] = prompts
    _save_and_refresh(cfg)
    return {"status": "ok", "restart_required": True}


@router.get("/chromadb/info")
async def chromadb_info():
    cfg = RAGConfig.from_yaml()
    vs = VectorStore(
        collection_name=cfg.collection_name,
        persist_directory=cfg.persist_directory,
        embedding_function=None,
    )
    stats = vs.get_collection_stats()
    size_mb = _disk_usage_mb(cfg.persist_directory)
    version = "unknown"
    try:
        version = getattr(vs.client, "_client", {}).get("settings", {}).get("chroma_version", "unknown")
    except Exception:
        version = "unknown"
    return {
        "version": version,
        "persist_directory": cfg.persist_directory,
        "storage_mb": size_mb,
        "total_chunks": stats.get("count", 0),
        "status": "ready" if not stats.get("error") else "error",
        "metadata": stats.get("metadata", {}),
    }


@router.post("/global-knowledge/upload", status_code=status.HTTP_201_CREATED)
async def upload_global_knowledge(file: UploadFile = File(...), pipeline=Depends(get_ingestion_pipeline)):
    content = await file.read()
    path = knowledge_service.save_file(file.filename, content)
    result = pipeline.ingest_file(
        str(path),
        project_id=None,
        extra_metadata={"type": "global_knowledge", "document": file.filename},
    )
    chunk_count = 0
    if isinstance(result, dict):
        chunk_count = result.get("chunk_count") or result.get("chunks") or 0
    return {
        "filename": file.filename,
        "status": "ingested",
        "chunks": chunk_count,
        "restart_required": False,
    }


@router.get("/global-knowledge/files")
async def list_global_knowledge_files():
    docs = knowledge_service.list_documents()
    cfg = RAGConfig.from_yaml()
    vs = VectorStore(
        collection_name=cfg.collection_name,
        persist_directory=cfg.persist_directory,
        embedding_function=None,
    )
    rows: List[Dict[str, Any]] = []
    for doc in docs:
        chunk_count = vs.count_by_metadata({"type": "global_knowledge", "document": doc.filename})
        file_path = Path(GLOBAL_KNOWLEDGE_DIR) / doc.filename
        modified = file_path.stat().st_mtime if file_path.exists() else None
        rows.append({
            "filename": doc.filename,
            "size_bytes": doc.size_bytes,
            "chunks": chunk_count,
            "modified_ts": modified,
        })
    return {"files": rows}


@router.delete("/global-knowledge/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_global_knowledge(filename: str):
    removed = knowledge_service.delete_file(filename)
    if not removed:
        raise HTTPException(status_code=404, detail="File not found")
    cfg = RAGConfig.from_yaml()
    vs = VectorStore(
        collection_name=cfg.collection_name,
        persist_directory=cfg.persist_directory,
        embedding_function=None,
    )
    vs.delete_by_metadata({"type": "global_knowledge", "document": filename})
    return None
