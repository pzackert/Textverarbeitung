import pytest
from pathlib import Path
from src.parsers.xlsx_parser import XlsxParser
from src.parsers.exceptions import CorruptedFileError

@pytest.fixture
def xlsx_parser():
    return XlsxParser()

def test_xlsx_parser_init(xlsx_parser):
    assert xlsx_parser is not None
    assert xlsx_parser.supported_formats == ['xlsx']

def test_xlsx_parser_accepts_xlsx(xlsx_parser):
    assert xlsx_parser.accepts_format('data.xlsx') == True

def test_xlsx_parser_rejects_non_xlsx(xlsx_parser):
    assert xlsx_parser.accepts_format('data.pdf') == False
    assert xlsx_parser.accepts_format('data.docx') == False
    assert xlsx_parser.accepts_format('data.csv') == False

def test_xlsx_parser_missing_file(xlsx_parser):
    with pytest.raises(FileNotFoundError):
        xlsx_parser.parse('nonexistent.xlsx')

def test_xlsx_parser_invalid_xlsx(xlsx_parser, tmp_path):
    invalid_xlsx = tmp_path / 'invalid.xlsx'
    invalid_xlsx.write_text('This is not an XLSX')
    with pytest.raises(CorruptedFileError):
        xlsx_parser.parse(str(invalid_xlsx))
