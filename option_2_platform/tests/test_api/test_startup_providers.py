import asyncio
import types
import sys
import yaml
import pytest
import requests

from src.core import config as core_config
from src.services import system_state as ss


class DummyCollection:
    def count(self):
        return 3


class DummyVectorStore:
    def __init__(self, collection_name: str, persist_directory: str = "data/chromadb"):
        self.collection = DummyCollection()


def _make_config(tmp_path):
    cfg = {
        "llm": {
            "provider": "ollama",
            "model": "qwen2.5:7b",
            "temperature": 0.2,
            "max_tokens": 1024,
            "timeout": 60,
            "lm_studio": {"models_dir": str(tmp_path / "lm_models"), "endpoint": "http://127.0.0.1:1234"},
            "ollama": {"models_dir": str(tmp_path / "ollama_models"), "endpoint": "http://127.0.0.1:11434"},
        },
        "rag": {
            "chunk_size": 500,
            "chunk_overlap": 50,
            "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "top_k": 5,
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
        "startup": {"timeout_per_step_sec": 5, "fallback_to_ollama": True},
    }
    path = tmp_path / "config.yaml"
    path.write_text(yaml.safe_dump(cfg, allow_unicode=False, sort_keys=False))
    return path


def _stub_requests(lm_ok: bool, ollama_ok: bool, generation_ok: bool = True):
    def fake_get(url, timeout=5, **kwargs):
        if "1234" in url:  # LM Studio
            if lm_ok:
                return types.SimpleNamespace(status_code=200, json=lambda: {"data": [{"id": "lm-model"}]})
            raise requests.exceptions.ConnectionError("lm studio offline")
        if "11434" in url:  # Ollama
            if ollama_ok:
                return types.SimpleNamespace(status_code=200, json=lambda: {"models": [{"name": "ollama-model"}]})
            raise requests.exceptions.ConnectionError("ollama offline")
        return types.SimpleNamespace(status_code=404, json=lambda: {})

    def fake_post(url, json=None, timeout=5, **kwargs):
        if ("api/generate" in url or "v1/chat/completions" in url) and generation_ok:
            return types.SimpleNamespace(status_code=200, text="OK", json=lambda: {"response": "OK"})
        if "api/pull" in url or "api/show" in url:
            return types.SimpleNamespace(status_code=200, json=lambda: {})
        return types.SimpleNamespace(status_code=404, text="not found", json=lambda: {})

    return fake_get, fake_post


@pytest.fixture(autouse=True)
def _isolate_config(tmp_path, monkeypatch):
    cfg_path = _make_config(tmp_path)
    monkeypatch.setattr(core_config, "DEFAULT_CONFIG_PATH", cfg_path)
    core_config.invalidate_config_cache()
    ss.system_state.reset()
    yield
    core_config.invalidate_config_cache()
    ss.system_state.reset()


@pytest.fixture
def patch_vector_store(monkeypatch):
    dummy_module = types.SimpleNamespace(VectorStore=DummyVectorStore)
    monkeypatch.setitem(sys.modules, "src.rag.vector_store", dummy_module)
    return DummyVectorStore


def _run_startup(monkeypatch, get_fn, post_fn):
    monkeypatch.setattr(ss, "requests", types.SimpleNamespace(get=get_fn, post=post_fn))
    asyncio.run(ss.run_startup_sequence())
    return ss.system_state.get_status_dict()


def test_startup_both_providers_ready(monkeypatch, patch_vector_store):
    get_fn, post_fn = _stub_requests(lm_ok=True, ollama_ok=True)
    status = _run_startup(monkeypatch, get_fn, post_fn)
    assert status["status"] == "ready"
    comp = {c["name"]: c for c in status["components"]}
    assert comp["lm_studio"]["status"] == "ready"
    assert comp["ollama"]["status"] == "ready" or comp["ollama"]["status"] == "skipped"


def test_startup_only_lm_studio(monkeypatch, patch_vector_store):
    get_fn, post_fn = _stub_requests(lm_ok=True, ollama_ok=False)
    status = _run_startup(monkeypatch, get_fn, post_fn)
    assert status["status"] == "ready"
    comp = {c["name"]: c for c in status["components"]}
    assert comp["lm_studio"]["status"] == "ready"


def test_startup_only_ollama(monkeypatch, patch_vector_store):
    get_fn, post_fn = _stub_requests(lm_ok=False, ollama_ok=True)
    status = _run_startup(monkeypatch, get_fn, post_fn)
    assert status["status"] == "ready"
    comp = {c["name"]: c for c in status["components"]}
    assert comp["ollama"]["status"] == "ready"


def test_startup_none_available(monkeypatch, patch_vector_store):
    get_fn, post_fn = _stub_requests(lm_ok=False, ollama_ok=False)
    status = _run_startup(monkeypatch, get_fn, post_fn)
    assert status["status"] == "error"
    comp = {c["name"]: c for c in status["components"]}
    assert comp["lm_studio"]["status"] == "error" or comp["ollama"]["status"] == "error"
