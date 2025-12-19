import logging
from pathlib import Path
from typing import Iterable, List, Optional

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
            from docling.document_converter import (
                DocumentConverter,
                InputFormat,
                PdfFormatOption,
                WordFormatOption,
                ExcelFormatOption,
            )
            from docling.datamodel.pipeline_options import (
                ThreadedPdfPipelineOptions,
                ConvertPipelineOptions,
                OcrAutoOptions,
            )
            from docling.pipeline.threaded_standard_pdf_pipeline import (
                ThreadedStandardPdfPipeline,
            )
        except Exception as exc:  # pragma: no cover - runtime import guard
            raise ImportError(
                "docling is required. Install with `uv add docling docling-core`."
            ) from exc

        convert_opts = ConvertPipelineOptions(
            do_picture_classification=False,
            do_picture_description=False,
        )

        def make_pdf_opts(do_ocr: bool) -> ThreadedPdfPipelineOptions:
            return ThreadedPdfPipelineOptions(
                do_ocr=do_ocr,
                ocr_options=OcrAutoOptions(lang=["deu", "eng"], force_full_page_ocr=False),
                do_table_structure=False,
                generate_page_images=False,
                generate_picture_images=False,
                generate_table_images=False,
                generate_parsed_pages=False,
            )

        def make_converter(do_ocr: bool) -> DocumentConverter:
            format_options = {
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=ThreadedStandardPdfPipeline,
                    pipeline_options=make_pdf_opts(do_ocr),
                ),
                InputFormat.DOCX: WordFormatOption(
                    pipeline_options=convert_opts,
                ),
                InputFormat.XLSX: ExcelFormatOption(
                    pipeline_options=convert_opts,
                ),
            }
            return DocumentConverter(format_options=format_options)

        self._make_converter = make_converter

    def parse(self, file_path: str) -> List[Document]:
        path = Path(file_path)
        if path.suffix.lower().lstrip(".") not in self.supported_formats:
            raise ValueError(f"Unsupported file type: {path.suffix}")
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        # Heuristic: extremely large PDFs are assumed to contain text layers; skip OCR to avoid timeouts
        do_ocr = not (path.suffix.lower() == ".pdf" and path.stat().st_size > 10 * 1024 * 1024)
        converter = self._make_converter(do_ocr=do_ocr)
        result = converter.convert(str(path))
        doc = getattr(result, "document", None)
        if doc is None:
            raise ValueError("Docling conversion produced no document")

        page_texts: dict[int, List[str]] = {}
        page_bboxes: dict[int, Optional[BoundingBox]] = {}

        for node in self._iter_text_nodes(doc):
            text = node.text.strip()
            if not text:
                continue

            prov = getattr(node, "prov", []) or []
            bbox = self._bbox_from_prov(prov)
            page_no = prov[0].page_no if prov else 1

            page_texts.setdefault(page_no, []).append(text)
            if page_no not in page_bboxes and bbox:
                page_bboxes[page_no] = bbox

        if not page_texts:
            raise ValueError("Docling returned no blocks for document")

        blocks: List[Block] = []
        for page_no in sorted(page_texts.keys()):
            combined = "\n".join(page_texts[page_no]).strip()
            if not combined:
                continue
            blocks.append(
                Block(
                    text=combined,
                    bbox=page_bboxes.get(page_no),
                    block_type="page",
                    table_md=None,
                    docling_id=None,
                    page_number=page_no,
                )
            )

        full_text = "\n\n".join(block.text for block in blocks)
        page_count = max((b.page_number for b in blocks), default=1)
        metadata = {
            "page_count": page_count,
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

    def _iter_text_nodes(self, doc) -> Iterable:
        """Depth-first traversal that resolves RefItems and yields text-bearing nodes."""

        def resolve(node):
            return node.resolve(doc) if hasattr(node, "resolve") else node

        stack = list(getattr(doc.body, "children", []) or [])
        while stack:
            raw = stack.pop(0)
            node = resolve(raw)
            if getattr(node, "text", None):
                yield node
            children = getattr(node, "children", None) or []
            stack.extend(children)

    def _bbox_from_prov(self, prov_list) -> Optional[BoundingBox]:
        if not prov_list:
            return None

        first = prov_list[0]
        bbox_val = getattr(first, "bbox", None)
        if bbox_val is None:
            return None

        try:
            return BoundingBox(
                page=first.page_no,
                x0=float(bbox_val.l),
                y0=float(bbox_val.b),
                x1=float(bbox_val.r),
                y1=float(bbox_val.t),
                page_width=float(getattr(bbox_val, "page_width", 0.0)),
                page_height=float(getattr(bbox_val, "page_height", 0.0)),
            )
        except Exception:
            return None