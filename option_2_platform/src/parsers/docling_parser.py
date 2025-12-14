import logging
from pathlib import Path
from typing import List, Optional

from src.parsers.models import Document, Block, BoundingBox

logger = logging.getLogger(__name__)


class DoclingParser:
    """Docling-based parser for PDF, DOCX, XLSX with layout and provenance."""

    supported_formats = {"pdf", "docx", "xlsx"}

    def __init__(self, converter_cls=None) -> None:
        if converter_cls is not None:
            self.converter_cls = converter_cls
            return

        try:
            # Lazy import so unit tests can mock without docling installed
            from docling.document_converter import DocumentConverter
        except Exception as exc:  # pragma: no cover - runtime import guard
            raise ImportError(
                "docling is required. Install with `uv add docling docling-core`."
            ) from exc

        self.converter_cls = DocumentConverter

    def parse(self, file_path: str) -> List[Document]:
        path = Path(file_path)
        if path.suffix.lower().lstrip(".") not in self.supported_formats:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        converter = self.converter_cls()
        result = converter.convert(str(path))

        blocks: List[Block] = []
        all_text_parts: List[str] = []

        pages = getattr(result, "pages", []) or getattr(result, "document", [])
        for page_index, page in enumerate(pages):
            width = self._extract_dim(page, "width")
            height = self._extract_dim(page, "height")
            elements = getattr(page, "elements", []) or getattr(page, "blocks", [])

            for element in elements:
                text, table_md, block_type = self._extract_text(element)
                if not text and not table_md:
                    continue

                bbox = self._extract_bbox(element, page_index, width, height)
                block = Block(
                    text=text or table_md or "",
                    bbox=bbox,
                    block_type=block_type,
                    table_md=table_md,
                    docling_id=getattr(element, "id", None),
                    page_number=page_index + 1,
                )
                blocks.append(block)
                if text:
                    all_text_parts.append(text)
                if table_md:
                    all_text_parts.append(table_md)

        if not blocks:
            raise ValueError("Docling returned no blocks for document")

        full_text = "\n\n".join(all_text_parts)
        metadata = {
            "page_count": len(pages),
            "file_size": path.stat().st_size,
        }

        return [
            Document(
                content=full_text,
                metadata=metadata,
                source_file=str(path),
                file_type=path.suffix.lstrip("."),
                blocks=blocks,
            )
        ]

    def _extract_dim(self, page, attr: str) -> Optional[float]:
        return (
            getattr(page, attr, None)
            or getattr(page, f"page_{attr}", None)
            or getattr(getattr(page, "size", None), attr, None)
        )

    def _extract_bbox(
        self,
        element,
        page_index: int,
        page_width: Optional[float],
        page_height: Optional[float],
    ) -> Optional[BoundingBox]:
        bbox_val = getattr(element, "bbox", None) or getattr(element, "bounding_box", None)
        if bbox_val is None:
            return None

        # Support list/tuple or object with coords
        if isinstance(bbox_val, (list, tuple)) and len(bbox_val) >= 4:
            x0, y0, x1, y1 = bbox_val[:4]
        else:
            x0 = getattr(bbox_val, "x0", None)
            y0 = getattr(bbox_val, "y0", None)
            x1 = getattr(bbox_val, "x1", None)
            y1 = getattr(bbox_val, "y1", None)

        if None in (x0, y0, x1, y1):
            return None

        return BoundingBox(
            page=page_index + 1,
            x0=float(x0),
            y0=float(y0),
            x1=float(x1),
            y1=float(y1),
            page_width=float(page_width) if page_width else 0.0,
            page_height=float(page_height) if page_height else 0.0,
        )

    def _extract_text(self, element):
        # Heuristic extraction to avoid tight coupling to docling internals
        text = getattr(element, "text", None) or getattr(element, "content", None)
        table_md = getattr(element, "markdown", None)
        block_type = getattr(element, "type", None) or getattr(element, "category", "paragraph")
        if table_md:
            block_type = "table"
        return text, table_md, block_type or "paragraph"