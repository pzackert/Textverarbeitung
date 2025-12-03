import sys
import time
import logging
from pathlib import Path
from typing import List

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from src.rag.llm_chain import create_llm_chain

# Configure logging
logging.basicConfig(level=logging.ERROR) # Only errors for clean output

TEST_QUESTIONS = [
    "Was ist das IFB PROFI Programm?",
    "Welche Förderquoten gibt es?",
    "Wer ist antragsberechtigt?",
    "Wie hoch ist die maximale Fördersumme?",
    "Welche Projektformen werden gefördert?"
]

def main():
    print("Starting Batch Query Test")
    print("=" * 50)
    
    try:
        chain = create_llm_chain()
    except Exception as e:
        print(f"Initialization failed: {e}")
        return

    if not chain.llm_provider.is_available():
        print("❌ Ollama not available. Aborting batch test.")
        return

    results = []
    total_time = 0
    
    for i, question in enumerate(TEST_QUESTIONS, 1):
        print(f"\nQuery {i}/{len(TEST_QUESTIONS)}: {question}")
        print("-" * 30)
        
        try:
            start = time.time()
            result = chain.query(question)
            duration = time.time() - start
            total_time += duration
            
            print(f"Time: {duration:.2f}s")
            print(f"Answer length: {len(result['answer'])} chars")
            print(f"Citations: {len(result['citations'])}")
            print(f"Sources retrieved: {len(result['sources'])}")
            
            results.append({
                "question": question,
                "status": "success",
                "duration": duration
            })
            
        except Exception as e:
            print(f"❌ Failed: {e}")
            results.append({
                "question": question,
                "status": "failed",
                "error": str(e)
            })

    # Summary
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    
    successful = [r for r in results if r['status'] == 'success']
    avg_time = total_time / len(successful) if successful else 0
    
    print(f"Total Queries: {len(TEST_QUESTIONS)}")
    print(f"Successful:    {len(successful)}")
    print(f"Failed:        {len(results) - len(successful)}")
    print(f"Avg Time:      {avg_time:.2f}s")

if __name__ == "__main__":
    main()
