import sys
import os
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.rag.config import RAGConfig
from src.rag.llm_provider import OllamaProvider

def main():
    print("Testing Ollama Connection...")
    print("-" * 30)

    # Load config
    try:
        config = RAGConfig.from_yaml()
        print(f"Configuration loaded:")
        print(f"  Provider: {config.llm_provider}")
        print(f"  Model:    {config.llm_model}")
        print(f"  URL:      {config.llm_base_url}")
    except Exception as e:
        print(f"Error loading configuration: {e}")
        return

    # Initialize Provider
    provider = OllamaProvider(
        model_name=config.llm_model,
        base_url=config.llm_base_url
    )

    # Test Connection
    print("\nChecking connection status...")
    status = provider.test_connection()
    
    if status["available"]:
        print("✅ Connection Status: OK")
        print(f"ℹ️  {status['model_info']}")
        
        # Test Generation
        print("\nSending test prompt...")
        test_prompt = "Hello, are you ready to help with document analysis? Answer with 'Yes, I am ready.' only."
        try:
            response = provider.generate(
                prompt=test_prompt,
                max_tokens=50,
                temperature=0.1
            )
            print(f"🤖 Response: {response}")
        except Exception as e:
            print(f"❌ Generation failed: {e}")
    else:
        print("❌ Connection Status: FAILED")
        print(f"Error: {status['error']}")
        print("\nTroubleshooting:")
        print("1. Ensure Ollama is running: 'ollama serve'")
        print(f"2. Ensure model is pulled: 'ollama pull {config.llm_model}'")
        print(f"3. Check URL in config: {config.llm_base_url}")

if __name__ == "__main__":
    main()
