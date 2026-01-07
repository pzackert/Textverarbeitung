import csv
import logging
from pathlib import Path
from typing import List

from src.parsers.models import Document, Block

logger = logging.getLogger(__name__)


class CSVParser:
    """Lightweight CSV parser that preserves row order as table-like blocks."""

    supported_formats = {"csv"}

    def parse(self, file_path: str) -> List[Document]:
        path = Path(file_path)
        if path.suffix.lower() != ".csv":
            raise ValueError(f"Unsupported file type: {path.suffix}")
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        try:
            with path.open(newline="", encoding="utf-8", errors="ignore") as handle:
                reader = csv.reader(handle)
                rows = [row for row in reader]
        except Exception as exc:
            logger.error(f"Failed to read CSV {path.name}: {exc}")
            raise

        # Drop entirely empty rows
        rows = [row for row in rows if any(cell.strip() for cell in row)]
        if not rows:
            raise ValueError("CSV contains no data")

        max_cols = max(len(r) for r in rows) if rows else 0
        row_texts = [" | ".join(cell.strip() for cell in row) for row in rows]

        blocks: List[Block] = []
        for idx, row_text in enumerate(row_texts, start=1):
            # Treat each row as a table block; page_number kept at 1 for CSVs
            blocks.append(
                Block(
                    text=row_text or "(leer)",
                    bbox=None,
                    block_type="table",
                    table_md=None,
                    docling_id=None,
                    page_number=1,
                )
            )

        content = "\n".join(row_texts).strip()
        if not content:
            raise ValueError("CSV produced empty content")

        metadata = {
            "page_count": 1,
            "row_count": len(rows),
            "column_count": max_cols,
            "file_size": path.stat().st_size,
        }

        return [
            Document(
                content=content,
                metadata=metadata,
                source_file=str(path),
                file_type="csv",
                blocks=blocks,
            )
        ]
