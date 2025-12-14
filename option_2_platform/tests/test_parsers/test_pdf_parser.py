import pytest
from src.parsers.docling_parser import DoclingParser


class _FakeBBox:
    def __init__(self):
        self.x0 = 0
        self.y0 = 0
        self.x1 = 10
        self.y1 = 20


class _FakeElement:
    def __init__(self, text="Hello"):
        self.text = text
        self.bbox = _FakeBBox()
        self.id = "el-1"
        self.type = "paragraph"


class _FakePage:
    def __init__(self):
        self.width = 200
        self.height = 400
        self.elements = [_FakeElement()]


class _FakeResult:
    def __init__(self):
        self.pages = [_FakePage()]


class _FakeConverter:
    def convert(self, path: str):
        return _FakeResult()


def test_docling_parser_accepts_pdf(tmp_path):
    parser = DoclingParser(converter_cls=_FakeConverter)
    pdf_file = tmp_path / "sample.pdf"
    pdf_file.write_text("fake")

    docs = parser.parse(str(pdf_file))

    assert len(docs) == 1
    assert docs[0].blocks
    block = docs[0].blocks[0]
    assert block.bbox.page_width == 200
    assert block.bbox.page_height == 400


def test_docling_parser_rejects_format():
    parser = DoclingParser(converter_cls=_FakeConverter)
    with pytest.raises(ValueError):
        parser.parse("document.txt")


def test_docling_parser_missing_file():
    parser = DoclingParser(converter_cls=_FakeConverter)
    with pytest.raises(FileNotFoundError):
        parser.parse("nonexistent.pdf")
