import yaml
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.services.system_state import system_state
from src.core import config as core_config


@pytest.fixture
def temp_config(tmp_path, monkeypatch):
    cfg = {
        "llm": {
            "provider": "ollama",
            "model": "qwen2.5:7b",
            "temperature": 0.7,
            "max_tokens": 2000,
            "timeout": 120,
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
    }
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg, allow_unicode=False, sort_keys=False))
    monkeypatch.setattr(core_config, "DEFAULT_CONFIG_PATH", cfg_path)
    core_config.invalidate_config_cache()

    # create dummy model files
    lm_dir = tmp_path / "lm_models"
    lm_dir.mkdir(parents=True, exist_ok=True)
    (lm_dir / "dummy-lm.bin").write_text("x")
    ollama_dir = tmp_path / "ollama_models"
    ollama_dir.mkdir(parents=True, exist_ok=True)
    (ollama_dir / "dummy-ollama.bin").write_text("y")

    # unblock middleware
    system_state.status = "ready"
    system_state.current_action = "Test ready"

    yield cfg_path
    core_config.invalidate_config_cache()
    system_state.reset()


def test_get_settings_returns_models(temp_config):
    client = TestClient(app)
    resp = client.get("/api/settings")
    assert resp.status_code == 200
    data = resp.json()
    assert data["llm"]["provider"] == "ollama"
    assert "available_models" in data
    assert any(m["provider"] == "lm_studio" for m in data["available_models"])


def test_update_llm_writes_config(temp_config):
    client = TestClient(app)
    payload = {"model": "new-model", "temperature": 0.3, "max_tokens": 1500, "timeout": 90, "provider": "lm_studio"}
    resp = client.post("/api/settings/llm", json=payload)
    assert resp.status_code == 200
    with open(core_config.DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
        updated = yaml.safe_load(f)
    assert updated["llm"]["model"] == "new-model"
    assert updated["llm"]["temperature"] == 0.3
    assert updated["llm"]["provider"] == "lm_studio"


def test_update_rag_and_prompts(temp_config):
    client = TestClient(app)
    resp_rag = client.post("/api/settings/rag", json={"chunk_size": 600, "chunk_overlap": 40, "top_k": 7})
    assert resp_rag.status_code == 200
    resp_prompts = client.post("/api/settings/prompts", json={
        "begruessung": "Hi",
        "global_chat_initial": "G",
        "antrags_chat_initial": "A",
        "antwort_richtlinie": "R",
        "kriterien_pruefung": "K",
    })
    assert resp_prompts.status_code == 200
    with open(core_config.DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
        updated = yaml.safe_load(f)
    assert updated["rag"]["chunk_size"] == 600
    assert updated["prompts"]["begruessung"] == "Hi"
