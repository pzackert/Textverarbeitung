import os
import requests
import logging
from pathlib import Path
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

def _is_model_file(path: Path) -> bool:
    return path.is_file() and not path.name.startswith(".")

def scan_local_files(provider: str, models_dir: str | None) -> List[Dict[str, str]]:
    """Scan a models directory and return a simple descriptor list."""
    if not models_dir:
        return []
    root = Path(os.path.expanduser(models_dir)).resolve()
    if not root.exists():
        return []
    models: List[Dict[str, str]] = []
    try:
        for entry in sorted(root.iterdir()):
            if _is_model_file(entry):
                size_mb = entry.stat().st_size / (1024 * 1024)
                models.append({
                    "name": entry.name,
                    "provider": provider,
                    "size": f"{size_mb:.1f} MB",
                    "source": "local_file"
                })
    except Exception as e:
        logger.warning(f"Error scanning local files for {provider}: {e}")
    return models

def fetch_ollama_models(base_url: str = "http://127.0.0.1:11434") -> List[Dict[str, str]]:
    """Fetch active models from Ollama API."""
    models = []
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            for m in data.get("models", []):
                name = m.get("name")
                # simplify size if available
                size_mb = m.get("size", 0) / (1024 * 1024)
                if name:
                    models.append({
                        "name": name,
                        "provider": "ollama",
                        "size": f"{size_mb:.1f} MB",
                        "source": "api"
                    })
    except Exception as e:
        logger.warning(f"Ollama API check failed: {e}")
    return models

def fetch_lm_studio_models(base_url: str = "http://127.0.0.1:1234") -> List[Dict[str, str]]:
    """Fetch active models from LM Studio API (OpenAI compat)."""
    models = []
    try:
        resp = requests.get(f"{base_url}/v1/models", timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            for m in data.get("data", []):
                name = m.get("id")
                if name:
                     models.append({
                        "name": name,
                        "provider": "lm_studio",
                        "size": "Unknown", # API doesnt always return size
                        "source": "api"
                    })
    except Exception as e:
        logger.warning(f"LM Studio API check failed: {e}")
    return models

def scan_all_models(llm_settings: Any) -> List[Dict[str, str]]:
    """
    Scan both provider directories AND query their APIs.
    Deduplicates by name+provider.
    """
    all_models: List[Dict[str, str]] = []
    seen = set()

    # Helpers to get config safely (handling dict or object)
    def get_conf(obj, key, default=None):
        if isinstance(obj, dict):
            return obj.get(key, default)
        return getattr(obj, key, default)

    lm_conf = get_conf(llm_settings, "lm_studio")
    ollama_conf = get_conf(llm_settings, "ollama")

    # 1. Live APIs (Prioritized)
    live_ollama = fetch_ollama_models(get_conf(ollama_conf, "endpoint", "http://127.0.0.1:11434") if ollama_conf else "http://127.0.0.1:11434")
    live_lm = fetch_lm_studio_models(get_conf(lm_conf, "endpoint", "http://127.0.0.1:1234") if lm_conf else "http://127.0.0.1:1234")

    for m in live_ollama + live_lm:
        key = f"{m['provider']}:{m['name']}"
        if key not in seen:
            seen.add(key)
            all_models.append(m)

    # 2. Local Files (Fallback/Supplement)
    local_lm = scan_local_files("lm_studio", get_conf(lm_conf, "models_dir"))
    local_ollama = scan_local_files("ollama", get_conf(ollama_conf, "models_dir"))

    for m in local_lm + local_ollama:
        # Avoid dupes if file name matches API name exactly
        key = f"{m['provider']}:{m['name']}"
        if key not in seen:
            seen.add(key)
            all_models.append(m)
            
    return all_models
