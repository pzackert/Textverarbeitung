import sys
import os
import logging
from typing import List, Dict, Any

# Mock classes to avoid full dependency chain issues in tmp execution
class MockRetrieval:
    def retrieve(self, query, top_k, metadata_filter=None):
        # Always return dummy docs to simulate retrieval
        return [
            {"content": "Das Projekt 'Test Multi' hat ein Budget von 50.000 EUR.", "metadata": {"source": "antrag.pdf", "page": 1}, "score": 0.9},
            {"content": "Der Antragsteller ist die 'Test GmbH'.", "metadata": {"source": "register.pdf", "page": 2}, "score": 0.8}
        ]

class MockLLM:
    def generate(self, prompt, max_tokens, temperature):
        # Simulate LLM behavior based on prompt constraints
        if "3+3" in prompt:
            if "Nutze ausschließlich" in prompt:
                return "Das steht nicht in den Dokumenten."
            else:
                return "Das ist 6."
        if "Hallo" in prompt:
             return "Hallo! Wie kann ich helfen?"
        return "Antwort basierend auf Kontext."

# Import critical components (adjust paths if needed)
sys.path.append("/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform")
from src.rag.prompts import PromptTemplate, format_context

def test_chat_logic():
    print("--- Test 1: Strict Refusal (3+3) ---")
    retrieval = MockRetrieval()
    llm = MockLLM()
    
    query = "Was ist 3+3?"
    results = retrieval.retrieve(query, top_k=2)
    
    # Use ACTUAL prompt template from codebase
    template = PromptTemplate.standard_query()
    context_str = format_context(results)
    prompt = template.format(query=query, context=context_str)
    
    response = llm.generate(prompt, 100, 0.7)
    print(f"Query: {query}")
    print(f"Response: {response}")
    print(f"Constraint Check: 'Nutze ausschließlich' in prompt? {'Yes' if 'Nutze ausschließlich' in prompt else 'No'}")
    
    print("\n--- Test 2: Ghost Sources ---")
    # In the actual app, sources are just taken from 'results'
    sources = [r['metadata']['source'] for r in results]
    print(f"Query: {query}")
    print(f"Response: {response}")
    print(f"Displayed Sources: {sources}")
    print("Issue: Sources are shown even if response implies they weren't used/needed.")

if __name__ == "__main__":
    test_chat_logic()
