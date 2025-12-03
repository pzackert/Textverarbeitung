import pytest
from pathlib import Path
from src.parsers.docx_parser import DocxParser
from src.parsers.exceptions import CorruptedFileError

@pytest.fixture
def docx_parser():
    return DocxParser()

def test_docx_parser_init(docx_parser):
    assert docx_parser is not None
    assert docx_parser.supported_formats == ['docx']

def test_docx_parser_accepts_docx(docx_parser):
    assert docx_parser.accepts_format('document.docx') == True

def test_docx_parser_rejects_non_docx(docx_parser):
    assert docx_parser.accepts_format('document.pdf') == False
    assert docx_parser.accepts_format('document.xlsx') == False
    assert docx_parser.accepts_format('document.txt') == False

def test_docx_parser_missing_file(docx_parser):
    with pytest.raises(FileNotFoundError):
        docx_parser.parse('nonexistent.docx')

def test_docx_parser_invalid_docx(docx_parser, tmp_path):
    invalid_docx = tmp_path / 'invalid.docx'
    invalid_docx.write_text('This is not a DOCX')
    with pytest.raises(CorruptedFileError):
        docx_parser.parse(str(invalid_docx))
