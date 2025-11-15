"""
Logging-Setup für IFB PROFI
Option 1: Einfaches Python-Logging
"""
import logging
import os
from pathlib import Path
import yaml


def load_config():
    """Lade Config aus config.yaml"""
    config_path = Path(__file__).parent.parent.parent / "config" / "config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def setup_logger(name: str = "ifb_profi") -> logging.Logger:
    """
    Erstelle Logger mit File- und Console-Handler
    
    Args:
        name: Name des Loggers
    
    Returns:
        Konfigurierter Logger
    """
    # Config laden
    config = load_config()
    log_config = config.get('logging', {})
    
    # Logger erstellen
    logger = logging.getLogger(name)
    
    # Level setzen
    level_str = log_config.get('level', 'INFO')
    level = getattr(logging, level_str, logging.INFO)
    logger.setLevel(level)
    
    # Formatter erstellen
    formatter = logging.Formatter(
        log_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    )
    
    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler
    log_file = log_config.get('log_file', 'logs/ifb_profi.log')
    log_path = Path(__file__).parent.parent.parent / log_file
    
    # Log-Verzeichnis erstellen
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    file_handler = logging.FileHandler(log_path, encoding='utf-8')
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Verhindere Duplikate
    logger.propagate = False
    
    logger.info(f"Logger '{name}' initialisiert (Level: {level_str})")
    return logger


# Standard-Logger für das gesamte Projekt
logger = setup_logger()


if __name__ == "__main__":
    # Test
    test_logger = setup_logger("test")
    test_logger.debug("Debug-Nachricht")
    test_logger.info("Info-Nachricht")
    test_logger.warning("Warnung")
    test_logger.error("Fehler")
    print("✓ Logger-Test erfolgreich - siehe logs/ifb_profi.log")
