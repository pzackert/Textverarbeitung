"""ChromaDB Vector Store mit sentence-transformers"""
from pathlib import Path
from typing import List, Dict, Any
import chromadb
from chromadb.config import Settings
from backend.utils.config import get_config_value
from backend.utils.logger import setup_logger

try:  # pragma: no cover - optional heavy dependency
    from sentence_transformers import SentenceTransformer
    _SENTENCE_IMPORT_ERROR = None
except Exception as exc:  # pragma: no cover - defensive fallback
    SentenceTransformer = None  # type: ignore
    _SENTENCE_IMPORT_ERROR = exc

logger = setup_logger(__name__)


class _FallbackEmbedder:
    """Very small deterministic embedder used when transformers missing."""

    def encode(self, texts, show_progress_bar=False):  # pragma: no cover - simple helper
        if isinstance(texts, str):
            texts = [texts]
        vectors = []
        for text in texts:
            text = text or ""
            length = float(len(text))
            checksum = float(sum(ord(ch) for ch in text) % 997)
            vectors.append([length, checksum])
        return vectors


class VectorStore:
    """ChromaDB Vector Store für RAG"""
    
    def __init__(self):
        chroma_path = get_config_value('rag.chroma_path', 'data/chromadb')
        Path(chroma_path).mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=chroma_path,
            settings=Settings(anonymized_telemetry=False)
        )
        
        collection_name = get_config_value('rag.collection_name', 'ifb_documents')
        self.collection = self.client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}
        )
        
        model_name = get_config_value(
            'rag.embedding_model',
            'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
        )
        if SentenceTransformer is None:
            logger.warning(
                "SentenceTransformer nicht verfuegbar, nutze Fallback-Embedder: %s",
                _SENTENCE_IMPORT_ERROR,
            )
            self.embedder = _FallbackEmbedder()
        else:
            logger.info(f"Lade Embedding-Model: {model_name}")
            self.embedder = SentenceTransformer(model_name)
        logger.info(f"✓ VectorStore initialisiert ({self.collection.count()} Dokumente)")
    
    def add_documents(self, texts: List[str], metadatas: List[Dict[str, Any]], ids: List[str]):
        """Füge Dokumente zur Collection hinzu"""
        if not texts:
            return
        
        embeddings_array = self.embedder.encode(texts, show_progress_bar=False)
        embeddings = embeddings_array.tolist() if hasattr(embeddings_array, 'tolist') else list(embeddings_array)
        
        self.collection.add(
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas,
            ids=ids
        )
        logger.info(f"✓ {len(texts)} Chunks hinzugefügt (Total: {self.collection.count()})")
    
    def search(self, query: str, top_k: int = 0) -> List[Dict[str, Any]]:
        """Suche ähnliche Dokumente"""
        if top_k == 0:
            top_k = get_config_value('rag.top_k', 3)
        
        query_vectors = self.embedder.encode([query])
        query_embedding = query_vectors[0]
        if hasattr(query_embedding, 'tolist'):
            query_embedding = query_embedding.tolist()
        else:
            query_embedding = list(query_embedding)
        results = self.collection.query(query_embeddings=[query_embedding], n_results=top_k)
        
        formatted_results = []
        if results and results.get('documents') and results['documents'][0]:
            for i in range(len(results['documents'][0])):
                result_item = {
                    'text': results['documents'][0][i],
                    'id': results['ids'][0][i]
                }
                if results.get('metadatas') and results['metadatas'][0]:
                    result_item['metadata'] = results['metadatas'][0][i]
                if results.get('distances') and results['distances'][0]:
                    result_item['distance'] = results['distances'][0][i]
                formatted_results.append(result_item)
        
        logger.info(f"✓ Gefunden: {len(formatted_results)} relevante Chunks")
        return formatted_results
    
    def clear_all(self):
        """Lösche alle Dokumente"""
        self.client.delete_collection(self.collection.name)
        self.collection = self.client.create_collection(
            name=self.collection.name,
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("✓ Alle Dokumente gelöscht")

