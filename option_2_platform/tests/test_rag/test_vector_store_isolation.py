import os
from pathlib import Path

from src.rag.vector_store import VectorStore
from src.rag.models import Chunk


class DummyEmbedding:
    def embed_batch(self, texts):
        return [[0.0] * 4 for _ in texts]

    def embed(self, text):
        return [0.0] * 4


def _chunk(project_id: str, name: str):
    return Chunk(
        content=f"content-{name}",
        metadata={"project_id": project_id, "source": f"{project_id}/{name}.txt"},
        embedding=[0.0] * 4,
    )


def test_delete_projects_except(tmp_path):
    store = VectorStore(
        collection_name=f"test_{os.urandom(3).hex()}",
        persist_directory=str(tmp_path),
        embedding_function=DummyEmbedding(),
    )

    # add chunks for p1, p2, and global (no project_id)
    store.add_chunks([
        _chunk("p1", "a"),
        _chunk("p1", "b"),
        _chunk("p2", "c"),
    ])
    # global chunk without project_id
    store.collection.add(
        documents=["global"],
        embeddings=[[0.0] * 4],
        metadatas=[{"type": "global_knowledge"}],
        ids=["global_1"],
    )

    deleted = store.delete_projects_except("p1")
    assert deleted == 1  # p2 only
    # p1 chunks remain
    assert store.count_by_metadata({"project_id": "p1"}) == 2
    # global chunk remains
    result = store.collection.get(where={"type": "global_knowledge"}, limit=None)
    ids = result.get("ids") or []
    if ids and isinstance(ids[0], list):
        ids = ids[0]
    assert ids


def test_delete_project(tmp_path):
    store = VectorStore(
        collection_name=f"test_{os.urandom(3).hex()}",
        persist_directory=str(tmp_path),
        embedding_function=DummyEmbedding(),
    )

    store.add_chunks([
        _chunk("p1", "a"),
        _chunk("p1", "b"),
    ])
    deleted = store.delete_project("p1")
    assert deleted == 2
    assert store.count_by_metadata({"project_id": "p1"}) == 0
