"""
Config-Loader for IFB PROFI Platform
"""
from pathlib import Path
import yaml
from typing import Dict, Any, Optional

_config_cache = None

def load_config(config_path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file
    """
    global _config_cache
    
    if _config_cache is not None and config_path is None:
        return _config_cache
    
    if config_path is None:
        # Assuming this file is in backend/core/config.py
        # Config is in ../../config/config.yaml
        path_obj = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    else:
        path_obj = Path(config_path)
    
    if not path_obj.exists():
        # Fallback or error
        print(f"Config file not found at {path_obj}")
        return {}

    with open(path_obj, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    if _config_cache is None:
        _config_cache = config
    
    return config

def get_config_value(key_path: str, default: Any = None) -> Any:
    """
    Get specific config value using dot notation (e.g. "llm.model")
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
