import sys
from pathlib import Path
from typing import List, Dict, Any, Optional

# Add project root to python path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

from unittest.mock import MagicMock
from src.rag.prompts import PromptTemplate, format_context
from src.rag.prompt_builder import PromptBuilder
from src.rag.retrieval import RetrievalEngine

def main():
    print("Prompt Template System Demo")
    print("=" * 50)
    
    # Setup
    mock_engine = MagicMock(spec=RetrievalEngine)
    mock_engine.retrieve.return_value = [
        {
            "content": "Die IFB Hamburg fördert innovative Vorhaben in Hamburg. Das PROFI Programm richtet sich an KMU.",
            "metadata": {"source": "Richtlinie_PROFI.pdf", "page": 3},
            "score": 0.95
        },
        {
            "content": "Antragsberechtigt sind Unternehmen mit Sitz oder Betriebsstätte in Hamburg. Die Förderung erfolgt als Zuschuss.",
            "metadata": {"source": "Richtlinie_PROFI.pdf", "page": 4},
            "score": 0.88
        }
    ]
    
    builder = PromptBuilder(retrieval_engine=mock_engine)
    
    # 1. Standard Query
    print("\n1. Standard Query Template")
    print("-" * 30)
    query = "Wer ist antragsberechtigt?"
    prompt = builder.build_query_prompt(query, template_type="standard")
    print(prompt)
    
    # 2. Criteria Evaluation
    print("\n2. Criteria Evaluation Template")
    print("-" * 30)
    criterion = "Unternehmen muss Sitz in Hamburg haben"
    prompt = builder.build_query_prompt(criterion, template_type="evaluation")
    print(prompt)
    
    # 3. Document Summary
    print("\n3. Document Summary Template")
    print("-" * 30)
    prompt = builder.build_query_prompt("Zusammenfassung", template_type="summary")
    print(prompt)

if __name__ == "__main__":
    main()
