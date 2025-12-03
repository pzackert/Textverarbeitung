import sys
import logging
from pathlib import Path

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.rag.llm_chain import create_llm_chain

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
# Silence some noisy loggers
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("chromadb").setLevel(logging.WARNING)

def main():
    print("\n" + "="*50)
    print("IFB PROFI - RAG System Demo")
    print("="*50 + "\n")
    
    try:
        chain = create_llm_chain()
    except Exception as e:
        print(f"❌ Initialization failed: {e}")
        return

    # Check if LLM is actually running
    if not chain.llm_provider.is_available():
        print("\n⚠️  Ollama is NOT running or reachable.")
        print(f"Please start Ollama: 'ollama serve'")
        print(f"And ensure model is pulled: 'ollama pull {chain.config.llm_model}'")
        print("\nYou can still type questions, but generation will fail.\n")
    else:
        print("\n✅ System ready. Type 'exit' or 'quit' to stop.\n")

    while True:
        try:
            question = input("\nFrage > ").strip()
            if question.lower() in ['exit', 'quit', 'q']:
                break
            if not question:
                continue
                
            print("\nThinking...", end="", flush=True)
            
            try:
                result = chain.query(question)
                print("\r", end="") # Clear "Thinking..."
                
                print("\n" + "-"*50)
                print(f"🤖 Antwort ({result['metadata']['duration']:.2f}s):")
                print("-"*50)
                print(result['answer'])
                print("-"*50)
                
                if result['citations']:
                    print("📚 Verwendete Quellen:")
                    for cit in result['citations']:
                        print(f"[{cit['number']}] {cit['source']} (Seite {cit.get('page', '?')})")
                elif result['sources']:
                    print("📚 Relevante Dokumente (aber nicht explizit zitiert):")
                    for i, src in enumerate(result['sources'], 1):
                        meta = src.get('metadata', {})
                        print(f"[{i}] {meta.get('source')} (Seite {meta.get('page', '?')})")
                        
            except Exception as e:
                print(f"\n❌ Error: {e}")
                
        except KeyboardInterrupt:
            break
            
    print("\nGoodbye!")

if __name__ == "__main__":
    main()
