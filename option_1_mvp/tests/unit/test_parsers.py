"""Test: Parser-Funktionen"""
import pytest
from pathlib import Path
from backend.parsers.pdf_parser import PDFParser
from backend.parsers.docx_parser import DOCXParser
from backend.parsers.xlsx_parser import XLSXParser
from backend.parsers.parser import parse_document
import pymupdf
from docx import Document
from openpyxl import Workbook


def test_pdf_parser(tmp_path):
    """Test PDF Parser"""
    # Create test PDF
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), "Test PDF Content")
    pdf_path = tmp_path / "test.pdf"
    doc.save(pdf_path)
    doc.close()
    
    # Parse
    parser = PDFParser()
    result = parser.parse(pdf_path)
    
    assert result["error"] is None
    assert "Test PDF Content" in result["text"]
    assert result["metadata"]["pages"] == 1


def test_docx_parser(tmp_path):
    """Test DOCX Parser"""
    # Create test DOCX
    doc = Document()
    doc.add_paragraph("Test DOCX Content")
    docx_path = tmp_path / "test.docx"
    doc.save(docx_path)
    
    # Parse
    parser = DOCXParser()
    result = parser.parse(docx_path)
    
    assert result["error"] is None
    assert "Test DOCX Content" in result["text"]


def test_xlsx_parser(tmp_path):
    """Test XLSX Parser"""
    # Create test XLSX
    wb = Workbook()
    ws = wb.active
    ws['A1'] = "Test XLSX Content"
    xlsx_path = tmp_path / "test.xlsx"
    wb.save(xlsx_path)
    
    # Parse
    parser = XLSXParser()
    result = parser.parse(xlsx_path)
    
    assert result["error"] is None
    assert "Test XLSX Content" in result["text"]


def test_parse_document_routing(tmp_path):
    """Test unified parse_document routing"""
    # PDF
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 50), "PDF Test")
    pdf_path = tmp_path / "test.pdf"
    doc.save(pdf_path)
    doc.close()
    
    result = parse_document(pdf_path)
    assert result["error"] is None
    assert "PDF Test" in result["text"]
    
    # Unsupported
    txt_path = tmp_path / "test.txt"
    result = parse_document(txt_path)
    assert result["error"] == "Datei nicht gefunden"
