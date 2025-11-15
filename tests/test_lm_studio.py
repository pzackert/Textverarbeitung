"""
LM Studio Connection Test
Prüft, ob LM Studio läuft und erreichbar ist
"""
import requests
from backend.utils.config import get_config_value
from backend.utils.logger import setup_logger

logger = setup_logger(__name__)


def test_lm_studio_connection():
    """
    Teste Verbindung zu LM Studio
    
    Returns:
        True wenn erfolgreich, False sonst
    """
    base_url = get_config_value("llm.base_url", "http://localhost:1234/v1")
    
    try:
        # Teste /models Endpoint
        response = requests.get(f"{base_url}/models", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            logger.info(f"✓ LM Studio erreichbar unter {base_url}")
            logger.info(f"  Verfügbare Modelle: {len(models.get('data', []))}")
            
            for model in models.get('data', []):
                logger.info(f"    - {model.get('id', 'Unknown')}")
            
            return True
        else:
            logger.error(f"✗ LM Studio antwortet mit Status {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        logger.error(f"✗ Kann LM Studio nicht erreichen unter {base_url}")
        logger.error("  → Bitte LM Studio starten und ein Modell laden")
        logger.error("  → Download: https://lmstudio.ai/")
        logger.error("  → Empfohlenes Modell: Qwen2.5-4B-Instruct (GGUF)")
        return False
        
    except Exception as e:
        logger.error(f"✗ Fehler beim Testen der Verbindung: {e}")
        return False


if __name__ == "__main__":
    print("\n=== LM Studio Connection Test ===\n")
    success = test_lm_studio_connection()
    
    if success:
        print("\n✓ LM Studio ist bereit!")
    else:
        print("\n✗ LM Studio ist nicht verfügbar")
        print("\nManuelle Setup-Schritte:")
        print("1. LM Studio herunterladen: https://lmstudio.ai/")
        print("2. Qwen2.5-4B-Instruct Modell herunterladen")
        print("3. Modell laden und Server starten (localhost:1234)")
        print("4. Diesen Test erneut ausführen\n")
