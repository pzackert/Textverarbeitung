from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

MODEL_NAME = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

def debug_similarity():
    print(f"Loading model {MODEL_NAME}...")
    model = SentenceTransformer(MODEL_NAME)
    
    query = "Wer bist du?"
    doc = "Ich bin Herbert, der Sachbearbeiter für Förderanträge bei der IFB Hamburg."
    
    emb_q = model.encode([query])
    emb_d = model.encode([doc])
    
    sim = cosine_similarity(emb_q, emb_d)[0][0]
    dist = 1.0 - sim
    
    print(f"Query: {query}")
    print(f"Doc: {doc}")
    print(f"Similarity: {sim:.4f}")
    print(f"Distance: {dist:.4f}")

if __name__ == "__main__":
    debug_similarity()
