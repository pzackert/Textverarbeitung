from typing import List, Optional

try:
    # Optional dependency to match requested splitter behavior
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except Exception:  # pragma: no cover - fallback path when dependency missing
    RecursiveCharacterTextSplitter = None

from src.parsers.models import Document, Block
from src.rag.models import Chunk


class Chunker:
    """Docling-first chunker with fallback splitting for oversized blocks."""

    def __init__(
        self,
        chunk_size: int = 500,
        chunk_overlap: int = 50,
        max_tokens: int = 800,
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.max_tokens = max_tokens
        self.separators = ["\n\n", "\n", ". ", " ", ""]
        self._text_splitter = self._build_text_splitter()

    def split(self, document: Document) -> List[Chunk]:
        if not document.blocks:
            # Fallback to legacy behavior if no block info
            return self._split_text(document.content, document.metadata)

        final_chunks: List[Chunk] = []
        for block_idx, block in enumerate(document.blocks):
            block_text = block.text or ""
            block_tokens = self._estimate_tokens(block_text)

            if block_tokens > self.max_tokens:
                sub_chunks = self._split_block_text(block_text)
                for split_idx, sub_text in enumerate(sub_chunks):
                    final_chunks.append(
                        self._build_chunk(
                            sub_text,
                            document,
                            block,
                            chunk_index=len(final_chunks),
                            inherited_bbox=True,
                        )
                    )
            else:
                final_chunks.append(
                    self._build_chunk(
                        block_text,
                        document,
                        block,
                        chunk_index=len(final_chunks),
                        inherited_bbox=False,
                    )
                )

        total = len(final_chunks)
        for i, ch in enumerate(final_chunks):
            ch.metadata["chunk_index"] = i
            ch.metadata["total_chunks"] = total
            ch.metadata["chunk_size"] = self.chunk_size
            ch.metadata["chunk_overlap"] = self.chunk_overlap
        return final_chunks

    def _build_chunk(
        self,
        text: str,
        document: Document,
        block: Block,
        chunk_index: int,
        inherited_bbox: bool,
    ) -> Chunk:
        metadata = document.metadata.copy()
        metadata.update({
            "source": document.source_file,
            "doc_type": document.file_type,
            "page_number": block.page_number,
            "block_type": block.block_type,
            "docling_id": block.docling_id,
            "table": block.block_type == "table",
            "chunk_id": chunk_index,
        })

        if block.table_md:
            metadata["table_md"] = block.table_md

        if block.bbox:
            metadata["bbox"] = {
                "page": block.bbox.page,
                "x0": block.bbox.x0,
                "y0": block.bbox.y0,
                "x1": block.bbox.x1,
                "y1": block.bbox.y1,
                "page_width": block.bbox.page_width,
                "page_height": block.bbox.page_height,
            }
            metadata["page_width"] = block.bbox.page_width
            metadata["page_height"] = block.bbox.page_height

        metadata["inherited_bbox"] = inherited_bbox

        return Chunk(content=text, metadata=metadata)

    def _split_block_text(self, text: str) -> List[str]:
        """Split a single Docling block while preserving parent metadata."""
        if self._text_splitter:
            return self._text_splitter.split_text(text)
        return self._split_text_with_overlap(text, self.separators)

    def _build_text_splitter(self):
        if RecursiveCharacterTextSplitter is None:
            return None
        return RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=self.separators,
        )

    def _split_text(self, text: str, base_metadata: Optional[dict] = None) -> List[Chunk]:
        parts = self._split_text_with_overlap(text, self.separators)
        chunks: List[Chunk] = []
        for idx, part in enumerate(parts):
            meta = (base_metadata or {}).copy()
            meta.update({
                "chunk_index": idx,
                "chunk_id": idx,
                "total_chunks": len(parts),
            })
            chunks.append(Chunk(content=part, metadata=meta))
        return chunks

    def _split_text_with_overlap(self, text: str, separators: List[str]) -> List[str]:
        final_chunks: List[str] = []

        separator = separators[-1]
        new_separators: List[str] = []
        for i, sep in enumerate(separators):
            if sep == "":
                separator = ""
                break
            if sep in text:
                separator = sep
                new_separators = separators[i + 1 :]
                break

        splits = text.split(separator) if separator else list(text)

        docs: List[str] = []
        current_doc: List[str] = []
        total = 0
        sep_len = len(separator)

        def flush_current():
            if current_doc:
                doc = separator.join(current_doc)
                if doc:
                    docs.append(doc)

        for part in splits:
            part_len = len(part)
            projected = total + part_len + (sep_len if current_doc else 0)
            if projected > self.chunk_size and current_doc:
                flush_current()
                # handle overlap: keep tail
                while total > self.chunk_overlap and current_doc:
                    total -= len(current_doc[0]) + (sep_len if len(current_doc) > 1 else 0)
                    current_doc.pop(0)
            current_doc.append(part)
            total += part_len + (sep_len if len(current_doc) > 1 else 0)

            if part_len > self.chunk_size and new_separators:
                # split deeper
                docs.extend(self._split_text_with_overlap(part, new_separators))

        flush_current()
        final_chunks.extend(docs)
        return final_chunks

    def _estimate_tokens(self, text: str) -> int:
        # Cheap token estimate; avoids pulling tokenizer deps
        return max(1, len(text.split()))
