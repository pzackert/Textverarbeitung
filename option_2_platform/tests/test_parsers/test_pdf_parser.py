import pytest
from pathlib import Path
from src.parsers.pdf_parser import PDFParser
from src.parsers.exceptions import CorruptedFileError, UnsupportedFormatError

@pytest.fixture
def pdf_parser():
    return PDFParser()

def test_pdf_parser_init(pdf_parser):
    assert pdf_parser is not None
    assert pdf_parser.supported_formats == ['pdf']

def test_pdf_parser_accepts_pdf(pdf_parser):
    assert pdf_parser.accepts_format('document.pdf') == True

def test_pdf_parser_rejects_non_pdf(pdf_parser):
    assert pdf_parser.accepts_format('document.docx') == False
    assert pdf_parser.accepts_format('document.xlsx') == False
    assert pdf_parser.accepts_format('document.txt') == False

def test_pdf_parser_missing_file(pdf_parser):
    with pytest.raises(FileNotFoundError):
        pdf_parser.parse('nonexistent.pdf')

def test_pdf_parser_invalid_pdf(pdf_parser, tmp_path):
    invalid_pdf = tmp_path / 'invalid.pdf'
    invalid_pdf.write_text('This is not a PDF')
    with pytest.raises(CorruptedFileError):
        pdf_parser.parse(str(invalid_pdf))
