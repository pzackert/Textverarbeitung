import types
import yaml
import pytest
from pathlib import Path
from unittest.mock import patch

from src.core import config as core_config
from src.services import system_state as ss


class DummyResp:
    def __init__(self, status_code=200, json_data=None, text="OK"):
        self.status_code = status_code
        self._json = json_data or {}
        self.text = text

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")


class DummyVectorStore:
    def __init__(self, *args, **kwargs):
        self.collection = types.SimpleNamespace(count=lambda: 0)
        self.client = types.SimpleNamespace(_client={"settings": {"chroma_version": "test"}})


@pytest.fixture(autouse=True)
def reset_config_cache(monkeypatch):
    core_config.invalidate_config_cache()
    yield
    core_config.invalidate_config_cache()


def _write_cfg(tmp_path, model, temp, max_tokens, chunk_size, chunk_overlap, top_k, provider):
    cfg = {
        "llm": {
            "provider": provider,
            "model": model,
            "temperature": temp,
            "max_tokens": max_tokens,
            "timeout": 60,
            "lm_studio": {
                "models_dir": str(tmp_path / "lm_models"),
                "endpoint": "http://127.0.0.1:1234",
            },
            "ollama": {
                "models_dir": str(tmp_path / "ollama_models"),
                "endpoint": "http://127.0.0.1:11434",
            },
        },
        "rag": {
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "top_k": top_k,
            "persist_directory": str(tmp_path / "chromadb"),
            "collection_name": "ifb_documents",
        },
        "prompts": {
            "begruessung": "Hallo",
            "global_chat_initial": "GC",
            "antrags_chat_initial": "AC",
            "antwort_richtlinie": "AR",
            "kriterien_pruefung": "KP",
        },
        "startup": {
            "auto_load_rag": True,
            "timeout_per_step_sec": 5,
            "fallback_to_ollama": True,
        },
    }
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(cfg, allow_unicode=False, sort_keys=False))
    (tmp_path / "lm_models").mkdir(parents=True, exist_ok=True)
    (tmp_path / "lm_models" / f"{model}.bin").write_text("lm")
    (tmp_path / "ollama_models").mkdir(parents=True, exist_ok=True)
    (tmp_path / "ollama_models" / f"{model}.bin").write_text("ol")
    return path


def _mock_requests(model_name):
    def fake_get(url, timeout=5, *args, **kwargs):
        if url.endswith("/v1/models"):
            return DummyResp(200, {"data": [{"id": model_name}]})
        if url.endswith("/api/tags"):
            return DummyResp(200, {"models": [{"name": model_name}]})
        return DummyResp(200, {})

    def fake_post(url, json=None, timeout=5, *args, **kwargs):
        if url.endswith("/api/show"):
            return DummyResp(200, {})
        if url.endswith("/v1/chat/completions"):
            return DummyResp(200, {"choices": [{"message": {"content": "OK"}}]})
        if url.endswith("/api/generate"):
            return DummyResp(200, {"response": "OK"})
        return DummyResp(200, {})

    return fake_get, fake_post


@pytest.mark.parametrize("idx,provider", [(1, "lm_studio"), (2, "ollama"), (3, "lm_studio"), (4, "ollama"), (5, "lm_studio")])
def test_startup_with_multiple_configs(tmp_path, monkeypatch, idx, provider):
    model = f"model-{idx}"
    cfg_path = _write_cfg(
        tmp_path,
        model=model,
        temp=0.1 * idx,
        max_tokens=1000 + idx,
        chunk_size=400 + idx,
        chunk_overlap=40 + idx,
        top_k=3 + idx,
        provider=provider,
    )

    # Point default config to temp file
    monkeypatch.setattr(core_config, "DEFAULT_CONFIG_PATH", cfg_path)
    core_config.invalidate_config_cache()

    # Mock requests
    fake_get, fake_post = _mock_requests(model)
    monkeypatch.setattr(ss.requests, "get", fake_get)
    monkeypatch.setattr(ss.requests, "post", fake_post)

    # Mock VectorStore (patch import target path)
    monkeypatch.setattr("src.rag.vector_store.VectorStore", DummyVectorStore)

    # Mock scan models
    monkeypatch.setattr(ss, "scan_all_models", lambda llm: [{"name": model, "provider": provider}])

    ss.system_state.reset()
    # Run startup
    ss.run_startup_sequence_sync = getattr(ss, "run_startup_sequence_sync", None)
    # If async only, run via loop
    if ss.run_startup_sequence_sync:
        ss.run_startup_sequence_sync()
    else:
        import asyncio
        asyncio.get_event_loop().run_until_complete(ss.run_startup_sequence())

    status = ss.system_state.get_status_dict()
    assert status["status"] in ("ready", "error")  # should generally be ready
    assert status["components_dict"]["llm_model"]["status"] != "pending"
    assert status["components_dict"]["chromadb"]["status"] != "pending"

    # Ensure cache invalidation works for next iteration
    core_config.invalidate_config_cache()
