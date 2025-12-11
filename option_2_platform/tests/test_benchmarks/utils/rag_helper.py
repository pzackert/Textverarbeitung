"""RAG Benchmark helper utilities.

Provides a thin wrapper around the existing RAG pipeline to make
benchmark tests deterministic and metric-aware (ingestion + retrieval).
"""
from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import fitz  # type: ignore

from src.rag.config import RAGConfig
from src.rag.ingestion import IngestionPipeline
from src.rag.retrieval import RetrievalEngine
from src.rag.vector_store import VectorStore
from benchmarks.utils.llm_client import LLMClient


class RAGBenchmarkHelper:
    """Utility wrapper to ingest documents and run RAG queries for benchmarks."""

    def __init__(
        self,
        data_dir: Path | str,
        collection_name: str = "benchmarks",
        persist_directory: Optional[Path | str] = None,
    ) -> None:
        base_config = RAGConfig.from_yaml()
        persist_dir = (
            Path(persist_directory)
            if persist_directory is not None
            else Path(__file__).parent.parent / "data" / "chromadb_benchmark"
        )

        self.config = base_config.model_copy(
            update={
                "collection_name": collection_name,
                "persist_directory": str(persist_dir),
                "vector_store_path": str(persist_dir),
            }
        )

        self.data_dir = Path(data_dir)
        self.ingestion = IngestionPipeline(config=self.config)
        self.vector_store: VectorStore = self.ingestion.vector_store
        self.retrieval = RetrievalEngine(vector_store=self.vector_store, config=self.config)

    def ingest_documents(self, file_paths: Sequence[str], project_id: Optional[str] = None) -> Dict[str, Any]:
        """Ingest a list of documents and collect ingestion metrics."""
        start = time.perf_counter()
        total_chunks = 0
        chunk_lengths: List[int] = []
        per_file: List[Dict[str, Any]] = []
        embedding_time = 0.0

        for raw_path in file_paths:
            path = Path(raw_path)
            file_start = time.perf_counter()
            documents = self.ingestion._parse_document(path)  # noqa: SLF001
            chunks = self.ingestion._chunk_document(documents)  # noqa: SLF001

            for chunk in chunks:
                if project_id:
                    chunk.metadata["project_id"] = project_id
                chunk.metadata["doc_id"] = path.stem
                chunk.metadata["doc_name"] = path.name
                if "page_number" not in chunk.metadata:
                    chunk.metadata["page_number"] = 1
                chunk_lengths.append(len(chunk.content))

            total_chunks += len(chunks)
            store_start = time.perf_counter()
            ids = self.ingestion._store_chunks(chunks)  # noqa: SLF001
            store_end = time.perf_counter()
            embedding_time += store_end - store_start

            per_file.append(
                {
                    "file": str(path),
                    "chunks": len(chunks),
                    "chunk_ids": ids,
                    "duration_s": round(store_end - file_start, 3),
                }
            )

        duration = time.perf_counter() - start
        avg_chunk = round(sum(chunk_lengths) / len(chunk_lengths), 1) if chunk_lengths else 0.0

        return {
            "success": True,
            "documents_processed": len(file_paths),
            "chunk_count": total_chunks,
            "avg_chunk_size": avg_chunk,
            "embedding_time_s": round(embedding_time, 3),
            "duration_s": round(duration, 3),
            "files": per_file,
            "vector_store": self.vector_store.get_collection_stats(),
            "vector_store_size_mb": self._get_dir_size_mb(Path(self.config.persist_directory)),
        }

    def query(
        self,
        question: str,
        model_name: str,
        *,
        temperature: float = 0.0,
        max_tokens: int = 512,
        context_length: Optional[int] = None,
        top_k: Optional[int] = None,
        metadata_filter: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Run a RAG query and collect retrieval + generation metrics."""
        retrieval_start = time.perf_counter()
        results = self.retrieval.retrieve(
            query=question,
            top_k=top_k or self.config.top_k,
            metadata_filter=metadata_filter,
        )
        retrieval_time = time.perf_counter() - retrieval_start

        context = self.retrieval.format_context(results) if results else ""
        prompt = (
            "Nutze den folgenden Kontext, um die Frage präzise zu beantworten."
            " Antworte knapp und bleibe beim Kontext.\n\n"
            f"Kontext:\n{context}\n\nFrage: {question}\nAntwort:"
        )

        client = LLMClient(model_name)
        available = client.check_availability()
        if not available:
            return {
                "success": False,
                "error": "Model not available",
                "retrieval_time_s": round(retrieval_time, 3),
                "chunks_retrieved": len(results),
            }

        generation_start = time.perf_counter()
        llm_result = client.query(
            prompt,
            temperature=temperature,
            max_tokens=max_tokens,
            context_length=context_length,
        )
        generation_time = time.perf_counter() - generation_start
        total_time = retrieval_time + generation_time

        metrics = llm_result.get("metrics")
        return {
            "success": llm_result.get("success", False),
            "answer": llm_result.get("response", ""),
            "retrieval_time_s": round(retrieval_time, 3),
            "generation_time_s": metrics.response_time_s if metrics else round(generation_time, 3),
            "total_time_s": round(total_time, 3),
            "chunks_retrieved": len(results),
            "tokens_generated": llm_result.get("tokens_generated"),
            "tokens_per_sec": metrics.tokens_per_sec if metrics else None,
            "ram_used_mb": metrics.ram_used_mb if metrics else None,
            "cpu_percent": metrics.cpu_percent if metrics else None,
            "context_used": context_length,
            "results": results,
        }

    def get_document_stats(self, file_path: str) -> Dict[str, Any]:
        """Return basic PDF document statistics for large document tests."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        with fitz.open(str(path)) as doc:
            pages = len(doc)
            text = "".join(page.get_text() for page in doc)

        words = len(text.split())
        return {
            "pages": pages,
            "words": words,
            "size_bytes": path.stat().st_size,
            "size_mb": round(path.stat().st_size / (1024 * 1024), 2),
        }

    def clear_vectorstore(self) -> None:
        """Clear the benchmark vector store to avoid cross-test contamination."""
        self.vector_store.clear_collection()

    @staticmethod
    def _get_dir_size_mb(path: Path) -> float:
        total = 0
        for root, _, files in os.walk(path):
            for name in files:
                try:
                    total += (Path(root) / name).stat().st_size
                except FileNotFoundError:
                    continue
        return round(total / (1024 * 1024), 2)
