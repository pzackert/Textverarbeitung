from src.rag.chunker import Chunker
from src.parsers.models import Document, Block, BoundingBox


def _make_doc_with_block(text: str, with_bbox: bool = True):
    bbox = BoundingBox(
        page=1,
        x0=0,
        y0=0,
        x1=10,
        y1=10,
        page_width=200,
        page_height=400,
    ) if with_bbox else None

    block = Block(text=text, bbox=bbox, block_type="paragraph", page_number=1)
    return Document(
        content=text,
        metadata={"source": "test.pdf"},
        source_file="test.pdf",
        file_type="pdf",
        blocks=[block],
    )


def test_docling_block_chunking_preserves_bbox():
    doc = _make_doc_with_block("Hallo Welt")
    chunker = Chunker(chunk_size=100, chunk_overlap=10, max_tokens=50)

    chunks = chunker.split(doc)

    assert len(chunks) == 1
    assert chunks[0].metadata["bbox"]["page_width"] == 200
    assert chunks[0].metadata["bbox"]["page_height"] == 400


def test_hybrid_chunking_splits_large_block():
    text = "Wort " * 200  # ~200 tokens
    doc = _make_doc_with_block(text)
    chunker = Chunker(chunk_size=100, chunk_overlap=10, max_tokens=50)

    chunks = chunker.split(doc)

    assert len(chunks) > 1
    assert [c.metadata["chunk_index"] for c in chunks] == list(range(len(chunks)))
    for chunk in chunks:
        assert chunk.metadata["inherited_bbox"] is True
        assert chunk.metadata["page_number"] == 1
        bbox = chunk.metadata.get("bbox")
        assert bbox
        assert bbox["x0"] == 0
        assert bbox["y0"] == 0
        assert bbox["x1"] == 10
        assert bbox["y1"] == 10
        assert bbox["page_width"] == 200
        assert bbox["page_height"] == 400


def test_string_fallback_chunking():
    chunker = Chunker(chunk_size=20, chunk_overlap=5, max_tokens=50)
    chunks = chunker.split(Document(content="Kurz", metadata={}, source_file="", file_type="txt", blocks=[]))

    assert len(chunks) >= 1
    assert chunks[0].metadata.get("chunk_id") == 0
