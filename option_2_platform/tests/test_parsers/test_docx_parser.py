import pytest
from src.parsers.docling_parser import DoclingParser


class _FakeDocPage:
    def __init__(self):
        self.width = 100
        self.height = 200
        self.elements = []


class _FakeDocResult:
    def __init__(self):
        self.pages = [_FakeDocPage()]


class _FakeDocConverter:
    def convert(self, path: str):
        return _FakeDocResult()


def test_docling_parser_accepts_docx(tmp_path):
    parser = DoclingParser(converter_cls=_FakeDocConverter)
    docx_file = tmp_path / "sample.docx"
    docx_file.write_text("fake")

    docs = parser.parse(str(docx_file))
    assert len(docs) == 1
    assert docs[0].metadata.get("page_count") == 1


def test_docling_parser_rejects_wrong_format():
    parser = DoclingParser(converter_cls=_FakeDocConverter)
    with pytest.raises(ValueError):
        parser.parse("file.txt")


def test_docling_parser_missing_file_docx():
    parser = DoclingParser(converter_cls=_FakeDocConverter)
    with pytest.raises(FileNotFoundError):
        parser.parse("missing.docx")
