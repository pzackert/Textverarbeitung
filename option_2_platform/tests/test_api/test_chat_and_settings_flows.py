import json
import types
import yaml
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.api.dependencies import get_llm_chain
from src.core import config as core_config
from src.services.system_state import system_state


class FakeLLMChain:
    def __init__(self):
        self.llm_provider = types.SimpleNamespace(model_name="fake-model")
        self.config = types.SimpleNamespace(llm_model="fake-model")

    def query(self, question: str, template_type: str = "standard", top_k=None, system_prompt=None, metadata_filter=None, answer_guideline=None):
        return {
            "answer": f"ANSWER:{question}",
            "sources": [{"document": "dummy.pdf", "page": 1}],
            "citations": [],
            "metadata": {"duration": 0.01},
        }


@pytest.fixture(autouse=True)
def temp_config(tmp_path, monkeypatch):
    cfg = {
        "llm": {
            "provider": "ollama",
            "model": "qwen2.5:7b",
            "temperature": 0.3,
            "max_tokens": 2048,
            "timeout": 60,
            "lm_studio": {"models_dir": str(tmp_path / "lm_models"), "endpoint": "http://127.0.0.1:1234"},
            "ollama": {"models_dir": str(tmp_path / "ollama_models"), "endpoint": "http://127.0.0.1:11434"},
        },
        "rag": {
            "chunk_size": 800,
            "chunk_overlap": 80,
            "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
            "top_k": 8,
            "persist_directory": str(tmp_path / "chromadb"),
            "collection_name": "ifb_documents",
        },
        "prompts": {
            "begruessung": "EXTREME TEST GREETING",
            "global_chat_initial": "GLOBAL INIT PROMPT",
            "antrags_chat_initial": "AC",
            "antwort_richtlinie": "Kurz, präzise, deutsch.",
            "kriterien_pruefung": "KP",
        },
    }
    cfg_path = tmp_path / "config.yaml"
    cfg_path.write_text(yaml.safe_dump(cfg, allow_unicode=False, sort_keys=False), encoding="utf-8")
    monkeypatch.setattr(core_config, "DEFAULT_CONFIG_PATH", cfg_path)
    core_config.invalidate_config_cache()

    # dummy model files for listing
    (tmp_path / "lm_models").mkdir(parents=True, exist_ok=True)
    (tmp_path / "lm_models" / "lm-one.bin").write_text("x")
    (tmp_path / "ollama_models").mkdir(parents=True, exist_ok=True)
    (tmp_path / "ollama_models" / "ollama-one.bin").write_text("y")

    # unblock middleware
    system_state.status = "ready"
    system_state.current_action = "Test ready"

    yield cfg_path
    core_config.invalidate_config_cache()
    system_state.reset()
    app.dependency_overrides.clear()


@pytest.fixture
def client(monkeypatch):
    app.dependency_overrides[get_llm_chain] = lambda: FakeLLMChain()
    return TestClient(app)


def _read_config():
    with open(core_config.DEFAULT_CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_global_chat_seed_and_message_flow(client):
    # create chat -> should seed system + greeting
    resp = client.post("/api/chats/global/create")
    assert resp.status_code == 201
    data = resp.json()
    chat_id = data["chat_id"]

    # load chat and check seeded messages
    chat = client.get(f"/api/chats/global/{chat_id}").json()
    assert len(chat.get("messages", [])) == 2
    assert chat["messages"][0]["role"] == "system"
    assert "GLOBAL INIT PROMPT" in chat["messages"][0]["content"]
    assert chat["messages"][1]["role"] == "assistant"
    assert "EXTREME TEST GREETING" in chat["messages"][1]["content"]

    # send message without rag
    resp_msg = client.post(f"/api/chats/global/{chat_id}/message", json={"message": "hi", "include_rag": False})
    assert resp_msg.status_code == 200
    payload = resp_msg.json()
    assert payload["assistant_message"]["rag_used"] is False
    # total messages persisted
    chat_after = client.get(f"/api/chats/global/{chat_id}").json()
    assert len(chat_after.get("messages", [])) == 4

    # send message with rag (uses FakeLLMChain)
    resp_msg2 = client.post(f"/api/chats/global/{chat_id}/message", json={"message": "hello rag", "include_rag": True})
    assert resp_msg2.status_code == 200
    payload2 = resp_msg2.json()
    assert payload2["assistant_message"]["rag_used"] is True
    assert payload2["assistant_message"]["content"].startswith("ANSWER:")


def test_global_chat_list_and_delete(client):
    chat_ids = []
    for _ in range(3):
        r = client.post("/api/chats/global/create")
        chat_ids.append(r.json()["chat_id"])
    listing = client.get("/api/chats/global").json()
    assert listing["total_chats"] >= 3

    # delete one chat
    del_resp = client.delete(f"/api/chats/global/{chat_ids[0]}")
    assert del_resp.status_code == 200
    listing_after = client.get("/api/chats/global").json()
    remaining_ids = {c["chat_id"] for c in listing_after["chats"]}
    assert chat_ids[0] not in remaining_ids


def test_llm_hyperparams_multiple_profiles(client):
    profiles = [
        {"provider": "lm_studio", "model": "mistral-3b", "temperature": 0.7, "max_tokens": 10000, "timeout": 120},
        {"provider": "ollama", "model": "openai/gpt-oss-20b", "temperature": 0.5, "max_tokens": 20000, "timeout": 120},
        {"provider": "ollama", "model": "qwen3-vl-4b", "temperature": 0.2, "max_tokens": 4096, "timeout": 90},
    ]
    for p in profiles:
        resp = client.post("/api/settings/llm", json=p)
        assert resp.status_code == 200
        data = _read_config()
        for key in ["provider", "model", "temperature", "max_tokens", "timeout"]:
            assert data["llm"][key] == p[key]


def test_rag_profiles(client):
    cases = [
        {"chunk_size": 1000, "chunk_overlap": 50, "top_k": 10},
        {"chunk_size": 400, "chunk_overlap": 100, "top_k": 15},
        {"chunk_size": 2000, "chunk_overlap": 0, "top_k": 5},
    ]
    for case in cases:
        resp = client.post("/api/settings/rag", json=case)
        assert resp.status_code == 200
        data = _read_config()
        for k, v in case.items():
            assert data["rag"][k] == v


def test_prompt_update_reflected_in_new_chat(client):
    payload = {
        "begruessung": "NEUE BEGRUESSUNG",
        "global_chat_initial": "NEUER GLOBAL",
        "antrags_chat_initial": "AC2",
        "antwort_richtlinie": "ANTWORT KURZ",
        "kriterien_pruefung": "KP2",
    }
    resp = client.post("/api/settings/prompts", json=payload)
    assert resp.status_code == 200

    chat_resp = client.post("/api/chats/global/create")
    chat_id = chat_resp.json()["chat_id"]
    chat = client.get(f"/api/chats/global/{chat_id}").json()
    assert chat["messages"][0]["content"] == "NEUER GLOBAL"
    assert chat["messages"][1]["content"] == "NEUE BEGRUESSUNG"


def test_models_listing_combines_api_and_files(client, monkeypatch, tmp_path):
    # patch requests in model_scanner to provide live models
    from src.services import model_scanner

    def fake_get(url, timeout=2, **kwargs):
        if "v1/models" in url:
            return types.SimpleNamespace(status_code=200, json=lambda: {"data": [{"id": "live-lm"}]})
        if "api/tags" in url:
            return types.SimpleNamespace(status_code=200, json=lambda: {"models": [{"name": "live-ollama"}]})
        return types.SimpleNamespace(status_code=404, json=lambda: {})

    monkeypatch.setattr(model_scanner.requests, "get", fake_get)

    resp = client.get("/api/settings/models")
    assert resp.status_code == 200
    models = resp.json()["models"]
    names = {m["name"] for m in models}
    assert "live-lm" in names
    assert "live-ollama" in names
    assert "lm-one.bin" in names
    assert "ollama-one.bin" in names


def test_chat_sequence_multiple_chats_and_messages(client):
    # create two chats and interleave messages
    c1 = client.post("/api/chats/global/create").json()["chat_id"]
    c2 = client.post("/api/chats/global/create").json()["chat_id"]

    client.post(f"/api/chats/global/{c1}/message", json={"message": "hi c1", "include_rag": True})
    client.post(f"/api/chats/global/{c2}/message", json={"message": "hi c2", "include_rag": True})
    client.post(f"/api/chats/global/{c1}/message", json={"message": "again c1", "include_rag": False})

    chat1 = client.get(f"/api/chats/global/{c1}").json()
    chat2 = client.get(f"/api/chats/global/{c2}").json()

    assert len(chat1["messages"]) == 6  # 2 seeded + 2 user + 2 assistant
    assert len(chat2["messages"]) == 4

    # delete both
    client.delete(f"/api/chats/global/{c1}")
    client.delete(f"/api/chats/global/{c2}")
    listing = client.get("/api/chats/global").json()
    ids_left = {c["chat_id"] for c in listing.get("chats", [])}
    assert c1 not in ids_left and c2 not in ids_left
