"""
Vector Store implementation using ChromaDB.
Handles storage and retrieval of embeddings for RAG system.
"""
from typing import List, Dict, Optional, Any
import chromadb
from chromadb.config import Settings
from pathlib import Path
import logging
import uuid

from .models import Chunk
from .embeddings import EmbeddingGenerator
from .exceptions import RAGException

logger = logging.getLogger(__name__)

class VectorStore:
    """
    ChromaDB-based vector store for embeddings.
    
    Supports:
    - Persistent storage on disk
    - Metadata filtering
    - Semantic similarity search
    - Batch operations
    """
    
    def __init__(
        self,
        collection_name: str = "ifb_documents",
        persist_directory: str = "data/chromadb",
        embedding_function: Optional[EmbeddingGenerator] = None
    ):
        """
        Initialize vector store.
        
        Args:
            collection_name: Name of the ChromaDB collection
            persist_directory: Directory for persistent storage
            embedding_function: Optional custom embedding generator
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_function = embedding_function
        
        self._init_client(persist_directory)
        self._get_or_create_collection(collection_name)
        
    def _init_client(self, persist_directory: str):
        """Initialize ChromaDB client with persistence."""
        try:
            # Ensure directory exists
            Path(persist_directory).mkdir(parents=True, exist_ok=True)
            
            self.client = chromadb.PersistentClient(path=persist_directory)
            logger.info(f"Initialized ChromaDB client at {persist_directory}")
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise RAGException(f"Failed to initialize ChromaDB client: {e}")
            
    def _get_or_create_collection(self, collection_name: str):
        """Get existing collection or create new one."""
        try:
            # We don't pass embedding_function here because we handle embeddings manually
            # to use our optimized EmbeddingGenerator
            self.collection = self.client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"} # Use cosine similarity
            )
            logger.info(f"Accessed collection: {collection_name}")
        except Exception as e:
            logger.error(f"Failed to get/create collection {collection_name}: {e}")
            raise RAGException(f"Failed to get/create collection: {e}")

    def add_chunks(self, chunks: List[Chunk]) -> List[str]:
        """
        Add chunks with embeddings to vector store.
        
        Args:
            chunks: List of Chunk objects (already have content and metadata)
            
        Returns:
            List of IDs for added chunks
        """
        if not chunks:
            return []
            
        if not self.embedding_function:
            raise RAGException("Embedding function required to add chunks")
            
        try:
            # Prepare data for ChromaDB
            documents = [chunk.content for chunk in chunks]
            
            # Sanitize metadata (convert lists to strings)
            metadatas = []
            for chunk in chunks:
                meta = chunk.metadata.copy()
                for k, v in meta.items():
                    if isinstance(v, (list, dict)):
                        meta[k] = str(v)
                metadatas.append(meta)
            
            # Generate IDs: source_file_chunk_id or UUID if source missing
            ids = []
            for chunk in chunks:
                source = chunk.metadata.get("source", "unknown")
                chunk_id = chunk.metadata.get("chunk_id", uuid.uuid4().hex)
                page_num = chunk.metadata.get("page_number", "")
                row_num = chunk.metadata.get("row_number", "")
                sheet_name = chunk.metadata.get("sheet_name", "")
                
                # Create unique ID using project ID if available, else parent folder
                path_obj = Path(source)
                
                prefix = ""
                parts = path_obj.parts
                if "projects" in parts:
                    try:
                        idx = parts.index("projects")
                        if idx + 1 < len(parts):
                            prefix = parts[idx+1] # Project ID
                    except:
                        pass
                
                if not prefix and path_obj.parent.name and path_obj.parent.name != ".":
                    prefix = path_obj.parent.name
                
                safe_source = f"{prefix}_{path_obj.name}" if prefix else path_obj.name
                
                # Construct ID with available metadata
                id_parts = [safe_source]
                if page_num:
                    id_parts.append(f"p{page_num}")
                if sheet_name:
                    # Sanitize sheet name
                    safe_sheet = "".join(c for c in sheet_name if c.isalnum() or c in "_-")
                    id_parts.append(f"s{safe_sheet}")
                if row_num:
                    id_parts.append(f"r{row_num}")
                id_parts.append(str(chunk_id))
                
                ids.append("_".join(id_parts))
            
            # Generate embeddings
            embeddings = self.embedding_function.embed_batch(documents)
            
            # Add to collection
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=ids
            )
            
            logger.info(f"Added {len(chunks)} chunks to vector store")
            return ids
            
        except Exception as e:
            logger.error(f"Failed to add chunks to vector store: {e}")
            raise RAGException(f"Failed to add chunks to vector store: {e}")

    def add_chunk(self, chunk: Chunk) -> str:
        """Add single chunk (convenience method)."""
        return self.add_chunks([chunk])[0]

    def query(
        self,
        query_text: str,
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Query vector store for similar chunks.
        
        Args:
            query_text: Search query
            top_k: Number of results to return
            metadata_filter: Optional metadata filters
            
        Returns:
            List of results with content, metadata, and similarity scores
        """
        if not self.embedding_function:
            raise RAGException("Embedding function required for query")
            
        try:
            # Generate query embedding
            query_embedding = self.embedding_function.embed(query_text)
            
            return self.query_by_embedding(
                embedding=query_embedding,
                top_k=top_k,
                metadata_filter=metadata_filter
            )
        except Exception as e:
            logger.error(f"Query failed: {e}")
            raise RAGException(f"Query failed: {e}")

    def query_by_embedding(
        self,
        embedding: List[float],
        top_k: int = 5,
        metadata_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Query using pre-computed embedding."""
        try:
            results = self.collection.query(
                query_embeddings=[embedding],
                n_results=top_k,
                where=metadata_filter
            )
            
            # Format results
            formatted_results = []
            
            # ChromaDB returns lists of lists (one list per query)
            if results["ids"] and len(results["ids"]) > 0:
                ids = results["ids"][0]
                distances = results["distances"][0] if results["distances"] else []
                metadatas = results["metadatas"][0] if results["metadatas"] else []
                documents = results["documents"][0] if results["documents"] else []
                
                for i in range(len(ids)):
                    # Convert distance to similarity score (cosine distance -> similarity)
                    # ChromaDB cosine distance is 1 - cosine_similarity
                    # So similarity = 1 - distance
                    score = 1.0 - distances[i] if i < len(distances) else 0.0
                    
                    formatted_results.append({
                        "id": ids[i],
                        "score": score,
                        "content": documents[i] if i < len(documents) else "",
                        "metadata": metadatas[i] if i < len(metadatas) else {}
                    })
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Query by embedding failed: {e}")
            raise RAGException(f"Query by embedding failed: {e}")

    def get_collection_stats(self) -> Dict[str, Any]:
        """Get statistics about the collection."""
        try:
            count = self.collection.count()
            return {
                "count": count,
                "name": self.collection.name,
                "metadata": self.collection.metadata
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return {"error": str(e)}

    def clear_collection(self):
        """Clear all documents from collection."""
        try:
            # Delete all documents
            # ChromaDB doesn't have a direct 'clear', so we delete by ID or recreate
            # Deleting by empty where clause might not work in all versions
            # Recreating is safer
            self.client.delete_collection(self.collection_name)
            self._get_or_create_collection(self.collection_name)
            logger.info(f"Cleared collection: {self.collection_name}")
        except Exception as e:
            logger.error(f"Failed to clear collection: {e}")
            raise RAGException(f"Failed to clear collection: {e}")

    def delete_by_metadata(self, metadata_filter: Dict[str, Any]):
        """Delete documents matching metadata filter."""
        try:
            self.collection.delete(where=metadata_filter)
            logger.info(f"Deleted documents matching: {metadata_filter}")
        except Exception as e:
            logger.error(f"Failed to delete by metadata: {e}")
            raise RAGException(f"Failed to delete by metadata: {e}")
