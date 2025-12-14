from typing import Any, cast

from fastapi.testclient import TestClient

from src.api.main import app
from src.api.dependencies import get_llm_chain
from src.parsers.models import Document, Block, BoundingBox
from src.rag.chunker import Chunker
from src.rag.config import RAGConfig
from src.rag.ingestion import IngestionPipeline
from src.rag.retrieval import RetrievalEngine
from src.rag.vector_store import VectorStore


class DummyEmbeddingGenerator:
    def embed(self, text: str):
        return [0.1, 0.1, 0.1, 0.1]

    def embed_batch(self, texts):
        return [[0.1, 0.1, 0.1, 0.1] for _ in texts]


class DummyParser:
    def __init__(self, bbox: BoundingBox):
        self._bbox = bbox

    def parse(self, file_path: str):
        block = Block(
            text="Sample content for query",
            bbox=self._bbox,
            block_type="paragraph",
            page_number=self._bbox.page,
        )
        doc = Document(
            content=block.text,
            metadata={},
            source_file=file_path,
            file_type="pdf",
            blocks=[block],
        )
        return [doc]


class DummyPipeline(IngestionPipeline):
    def __init__(self, base_dir):
        self.config = RAGConfig()
        self.config.vector_store_path = str(base_dir)
        self.config.persist_directory = str(base_dir)
        self.config.collection_name = "test_api_collection"
        self.config.max_chunk_tokens = 10
        self.config.chunk_size = 50
        self.config.chunk_overlap = 0
        self._init_parsers()
        self._init_chunker()
        self._init_embedder()
        self._init_vector_store()

    def _init_parsers(self):
        bbox = BoundingBox(
            page=1,
            x0=10.5,
            y0=20.0,
            x1=110.0,
            y1=220.0,
            page_width=600.0,
            page_height=800.0,
        )
        self.parsers = {".pdf": DummyParser(bbox)}

    def _init_chunker(self):
        self.chunker = Chunker(
            chunk_size=self.config.chunk_size,
            chunk_overlap=self.config.chunk_overlap,
            max_tokens=self.config.max_chunk_tokens,
        )

    def _init_embedder(self):
        self.embedder = DummyEmbeddingGenerator()

    def _init_vector_store(self):
        self.vector_store = VectorStore(
            collection_name=self.config.collection_name,
            persist_directory=self.config.vector_store_path,
            embedding_function=cast(Any, self.embedder),
            schema_version=self.config.metadata_schema_version,
        )
        self.vector_store.ensure_schema(self.config.metadata_schema_version)


def test_query_response_contains_numeric_bbox(tmp_path):
    base_dir = tmp_path / "chroma"
    pipeline = DummyPipeline(base_dir)
    pdf_path = tmp_path / "sample.pdf"
    pdf_path.write_text("dummy")

    ingest_result = pipeline.ingest_file(str(pdf_path))
    assert ingest_result["success"] is True
    assert ingest_result["chunk_count"] >= 1

    retrieval = RetrievalEngine(vector_store=pipeline.vector_store, config=pipeline.config)

    class DummyLLMChain:
        def __init__(self, retrieval_engine):
            self.retrieval_engine = retrieval_engine

        def query(self, question: str, template_type: str = "standard", top_k: int = 5, system_prompt=None):
            results = self.retrieval_engine.retrieve(query=question, top_k=top_k or 1)
            return {"answer": "ready", "sources": results, "metadata": {"question": question}}

    dummy_chain = DummyLLMChain(retrieval)

    app.dependency_overrides[get_llm_chain] = lambda: dummy_chain
    client = TestClient(app)

    try:
        response = client.post("/query", json={"question": "Was steht im Dokument?", "top_k": 1})
        assert response.status_code == 200
        payload = response.json()
        assert payload["sources"]
        first = payload["sources"][0]

        assert first["bbox"]
        assert all(isinstance(v, (int, float)) for v in first["bbox"])
        assert isinstance(first["page_number"], int)
        assert isinstance(first["page_width"], (int, float))
        assert isinstance(first["page_height"], (int, float))
        assert first["bbox"][0] == 10.5
        assert first["page_width"] == 600.0
        assert first["page_height"] == 800.0
    finally:
        app.dependency_overrides.clear()
