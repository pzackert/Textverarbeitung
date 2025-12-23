import sys
from typing import List, Dict, Any

# Mock LLM (Simulated Behavior)
class MockLLM:
    def generate(self, prompt, max_tokens, temperature):
        if "3+3" in prompt:
            # New Hybrid Behavior
            if "Allgemeinwissen" in prompt: 
                return "Das ist 6." # Answer without citing sources
            return "Das steht nicht in den Dokumenten."
        if "Budget" in prompt:
            return "Das Budget beträgt 50.000 EUR [1]." # Answer using source
        return "Keine Ahnung."

# --- PROPOSED FIX: Hybrid Prompt & Source Filtering ---

class HybridPromptTemplate:
    @classmethod
    def hybrid_query(cls):
        system_prompt = (
            "Du bist ein hilfreicher Assistent für Förderanträge.\n"
            "Beantworte Fragen basierend auf den Dokumenten. "
            "Wenn die Frage NICHT mit den Dokumenten beantwortet werden kann, "
            "aber allgemeines Wissen (z.B. Rechnen, Begrüßung) erfordert, antworte direkt.\n"
            "WICHTIG: Wenn du Dokumente verwendest, zitiere sie IMMER als [1], [2] etc.\n"
            "Wenn du KEINE Dokumente verwendest (z.B. weil du aus Allgemeinwissen antwortest), zitiere NICHTS."
        )
        user_template = (
            "Kontext:\n{context}\n\nFrage: {query}\n\nAntwort:"
        )
        return cls(system_prompt, user_template)

    def __init__(self, system, user):
        self.system = system
        self.user = user
    
    def format(self, query, context):
        return f"{self.system}\n\n{self.user.format(query=query, context=context)}"

def filter_sources(answer: str, results: List[Dict]) -> List[Dict]:
    """Return sources ONLY if cited in answer (e.g. [1]) or if specific heuristic matches."""
    valid_sources = []
    
    # 1. Check for citations like [1], [2]...
    import re
    citations = re.findall(r'\[(\d+)\]', answer)
    indices = [int(c)-1 for c in citations if c.isdigit()]
    
    if indices:
        # Strict Mode: Only return cited sources
        for i in set(indices):
            if 0 <= i < len(results):
                valid_sources.append(results[i])
    else:
        # Fallback Logic:
        # If the answer is "I don't know" or "No info found", return NO sources.
        # If the answer looks like a valid answer (length > X) but no explicit citation, 
        # we might be in trouble. But our prompt instructs to cite.
        # Let's assume for Hybrid: No citation = No RAG used.
        pass

    return valid_sources

# --- TEST ---

def test_fix():
    print("--- Test Hybrid Fix ---")
    results = [
        {"content": "Budget: 50k", "metadata": {"source": "antrag.pdf"}, "score": 0.9},
        {"content": "Name: Test GmbH", "metadata": {"source": "reg.pdf"}, "score": 0.8}
    ]
    
    # 1. Formatting Context with Numbers
    context_str = ""
    for i, r in enumerate(results, 1):
        context_str += f"[{i}] {r['content']}\n"
    
    llm = MockLLM()
    template = HybridPromptTemplate.hybrid_query()
    
    # Case A: General Knowledge (3+3)
    query_a = "Was ist 3+3?"
    prompt_a = template.format(query_a, context_str)
    answer_a = llm.generate(prompt_a, 100, 0.7)
    sources_a = filter_sources(answer_a, results)
    
    print(f"Query: {query_a}")
    print(f"Answer: {answer_a}")
    print(f"Sources Shown: {[s['metadata']['source'] for s in sources_a]}")
    print(f"Result: {'PASS' if not sources_a else 'FAIL'}")
    
    print("\n")
    
    # Case B: Specific RAG (Budget)
    query_b = "Wie hoch ist das Budget?"
    prompt_b = template.format(query_b, context_str)
    answer_b = llm.generate(prompt_b, 100, 0.7)
    sources_b = filter_sources(answer_b, results)
    
    print(f"Query: {query_b}")
    print(f"Answer: {answer_b}")
    print(f"Sources Shown: {[s['metadata']['source'] for s in sources_b]}")
    print(f"Result: {'PASS' if 'antrag.pdf' in [s['metadata']['source'] for s in sources_b] else 'FAIL'}")

if __name__ == "__main__":
    test_fix()
