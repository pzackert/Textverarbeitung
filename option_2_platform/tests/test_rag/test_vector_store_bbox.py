import pytest
from src.rag.vector_store import VectorStore
from src.rag.embeddings import EmbeddingGenerator
from src.rag.models import Chunk


def test_vector_store_persists_bbox(tmp_path):
    # fresh store for test
    store_path = tmp_path / "chroma"
    embedder = EmbeddingGenerator(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    vs = VectorStore(
        collection_name="test_collection",
        persist_directory=str(store_path),
        embedding_function=embedder,
        schema_version="docling-v1",
    )
    vs.ensure_schema("docling-v1")

    chunk = Chunk(
        content="Hallo Welt",
        metadata={
            "source": "test.pdf",
            "page_number": 1,
            "bbox": {
                "page": 1,
                "x0": 0.0,
                "y0": 0.0,
                "x1": 10.0,
                "y1": 20.0,
                "page_width": 200.0,
                "page_height": 400.0,
            },
            "page_width": 200.0,
            "page_height": 400.0,
            "chunk_id": 0,
        },
    )

    ids = vs.add_chunks([chunk])
    assert len(ids) == 1

    results = vs.query("Hallo Welt", top_k=1)
    assert results
    meta = results[0]["metadata"]
    assert meta.get("bbox")
    assert meta.get("page_width") == 200.0
    assert meta.get("page_height") == 400.0