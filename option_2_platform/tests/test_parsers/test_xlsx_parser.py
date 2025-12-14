import pytest
from src.parsers.docling_parser import DoclingParser


class _FakeXlsxPage:
    def __init__(self):
        self.width = 120
        self.height = 300
        self.elements = []


class _FakeXlsxResult:
    def __init__(self):
        self.pages = [_FakeXlsxPage()]


class _FakeXlsxConverter:
    def convert(self, path: str):
        return _FakeXlsxResult()


def test_docling_parser_accepts_xlsx(tmp_path):
    parser = DoclingParser(converter_cls=_FakeXlsxConverter)
    xlsx_file = tmp_path / "sample.xlsx"
    xlsx_file.write_text("fake")

    docs = parser.parse(str(xlsx_file))
    assert docs[0].metadata.get("page_count") == 1


def test_docling_parser_rejects_wrong_format_xlsx():
    parser = DoclingParser(converter_cls=_FakeXlsxConverter)
    with pytest.raises(ValueError):
        parser.parse("file.csv")


def test_docling_parser_missing_file_xlsx():
    parser = DoclingParser(converter_cls=_FakeXlsxConverter)
    with pytest.raises(FileNotFoundError):
        parser.parse("missing.xlsx")
