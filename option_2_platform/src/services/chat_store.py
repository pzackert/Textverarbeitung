import json
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Any

BASE_DIR = Path(__file__).resolve().parents[2]
CHAT_DIR = BASE_DIR / "data" / "chats"
INPUT_DIR = BASE_DIR / "data" / "input"
CHAT_DIR.mkdir(parents=True, exist_ok=True)
INPUT_DIR.mkdir(parents=True, exist_ok=True)

ISO_FMT = "%Y-%m-%dT%H:%M:%SZ"

def _utc_now() -> str:
    return datetime.now(timezone.utc).strftime(ISO_FMT)


def _write_json(path: Path, payload: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with tmp_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    tmp_path.replace(path)


def _read_json(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


# ------------ Global Chat ------------

def create_global_chat() -> Dict[str, Any]:
    chat_id = uuid.uuid4().hex[:8]
    created_at = _utc_now()
    ts_part = created_at.replace(":", "").replace("-", "").replace("T", "_").replace("Z", "")
    file_path = CHAT_DIR / f"chat_{ts_part}_{chat_id}.json"
    chat = {
        "chat_id": chat_id,
        "type": "global",
        "created_at": created_at,
        "updated_at": created_at,
        "messages": [],
        "rag_active": True,
        "total_messages": 0,
        "file_path": str(file_path),
    }
    _write_json(file_path, chat)
    return chat


def list_global_chats() -> List[Dict[str, Any]]:
    chats: List[Dict[str, Any]] = []
    if not CHAT_DIR.exists():
        return []
    for path in sorted(CHAT_DIR.glob("chat_*.json")):
        try:
            data = _read_json(path)
            data["file_path"] = str(path)
            chats.append(data)
        except Exception:
            continue
    return chats


def load_global_chat(chat_id: str) -> Dict[str, Any]:
    for path in CHAT_DIR.glob(f"chat_*_{chat_id}.json"):
        data = _read_json(path)
        data["file_path"] = str(path)
        data["total_messages"] = len(data.get("messages", []))
        return data
    raise FileNotFoundError(f"Chat {chat_id} not found")


def save_global_chat(chat: Dict[str, Any]) -> Dict[str, Any]:
    file_path = Path(chat.get("file_path") or CHAT_DIR / f"chat_{chat['created_at']}_{chat['chat_id']}.json")
    chat["updated_at"] = _utc_now()
    chat["total_messages"] = len(chat.get("messages", []))
    chat["file_path"] = str(file_path)
    _write_json(file_path, chat)
    return chat


def delete_global_chat(chat_id: str) -> bool:
    """Delete a global chat by ID. Returns True if deleted, False if not found."""
    for path in CHAT_DIR.glob(f"chat_*_{chat_id}.json"):
        try:
            path.unlink()
            return True
        except Exception:
            pass
    return False


# ------------ Project Chat ------------

def _project_chat_path(project_id: str) -> Path:
    # Store project chat alongside project data
    return INPUT_DIR / project_id / "chat_history.json"


def load_or_create_project_chat(project_id: str) -> Dict[str, Any]:
    path = _project_chat_path(project_id)
    if path.exists():
        data = _read_json(path)
        data["file_path"] = str(path)
        return data
    created_at = _utc_now()
    path.parent.mkdir(parents=True, exist_ok=True)
    chat = {
        "project_id": project_id,
        "type": "project",
        "created_at": created_at,
        "updated_at": created_at,
        "messages": [],
        "total_messages": 0,
        "documents_loaded": [],
        "file_path": str(path),
    }
    _write_json(path, chat)
    return chat


def save_project_chat(chat: Dict[str, Any]) -> Dict[str, Any]:
    path = Path(chat.get("file_path") or _project_chat_path(chat["project_id"]))
    chat["updated_at"] = _utc_now()
    chat["total_messages"] = len(chat.get("messages", []))
    chat["file_path"] = str(path)
    _write_json(path, chat)
    return chat


def list_project_chats() -> List[Dict[str, Any]]:
    if not INPUT_DIR.exists():
        return []
    chats = []
    for path in INPUT_DIR.glob("*/chat_history.json"):
        try:
            data = _read_json(path)
            data["file_path"] = str(path)
            chats.append(data)
        except Exception:
            continue
    return chats
