"""
Config-Loader for IFB PROFI Platform
"""
from pathlib import Path
import yaml
from typing import Dict, Any, Optional

_config_cache = None
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "config.yaml"


def load_config(config_path: Optional[str] = None, force_reload: bool = False) -> Dict[str, Any]:
    """Load configuration from YAML file with optional cache bypass."""
    global _config_cache

    target_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH

    if not target_path.exists():
        print(f"Config file not found at {target_path}")
        return {}

    if _config_cache is not None and not force_reload and config_path is None:
        return _config_cache

    with open(target_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f) or {}

    if config_path is None:
        _config_cache = config

    return config


def save_config(data: Dict[str, Any], config_path: Optional[str] = None) -> None:
    """Persist configuration to YAML and refresh cache."""
    global _config_cache
    target_path = Path(config_path) if config_path else DEFAULT_CONFIG_PATH
    target_path.parent.mkdir(parents=True, exist_ok=True)
    with open(target_path, "w", encoding="utf-8") as f:
        yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)
    if config_path is None:
        _config_cache = data


def invalidate_config_cache():
    """Clear in-memory config cache."""
    global _config_cache
    _config_cache = None


def get_config_value(key_path: str, default: Any = None) -> Any:
    """Get specific config value using dot notation (e.g. "llm.model")."""
    config = load_config()
    keys = key_path.split(".")

    value: Any = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default

    return value
