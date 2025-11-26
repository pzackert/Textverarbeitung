"""
Config-Loader für IFB PROFI
"""
from pathlib import Path
import yaml
from typing import Dict, Any, Optional


_config_cache = None


def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Lade Konfiguration aus YAML-Datei
    
    Args:
        config_path: Pfad zur Config-Datei (optional, Default: config/config.yaml)
    
    Returns:
        Config als Dictionary
    """
    global _config_cache
    
    # Verwende Cache wenn vorhanden
    if _config_cache is not None and config_path is None:
        return _config_cache
    
    # Default-Pfad
    if config_path is None:
        path_obj = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    else:
        path_obj = Path(config_path)
    
    # Config laden
    with open(path_obj, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    # Cache setzen
    if _config_cache is None:
        _config_cache = config
    
    return config


def get_config_value(key_path: str, default: Any = None) -> Any:
    """
    Hole spezifischen Config-Wert mit Dot-Notation
    
    Args:
        key_path: Pfad zum Wert (z.B. "llm.model" oder "rag.chunk_size")
        default: Default-Wert falls nicht gefunden
    
    Returns:
        Config-Wert oder Default
    
    Example:
        >>> get_config_value("llm.model")
        "qwen2.5-4b-instruct"
    """
    config = load_config()
    keys = key_path.split('.')
    
    value = config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    
    return value


if __name__ == "__main__":
    # Test
    config = load_config()
    print("✓ Config geladen:")
    print(f"  LLM Provider: {get_config_value('llm.provider')}")
    print(f"  LLM Model: {get_config_value('llm.model')}")
    print(f"  RAG Chunk Size: {get_config_value('rag.chunk_size')}")
    print(f"  ChromaDB Path: {get_config_value('rag.chroma_path')}")
    print(f"  Logging Level: {get_config_value('logging.level')}")
