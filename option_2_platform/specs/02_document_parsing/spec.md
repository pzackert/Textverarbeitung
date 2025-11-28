# Document Parsing - Specification

## Goal
Implement a modular document parsing service capable of extracting structured text, tables, and metadata from PDF, DOCX, and XLSX files, ensuring high fidelity for RAG ingestion.

## Requirements

### Functional
- [ ] **Format Support**:
  - **PDF**: Extract text, preserve reading order, handle multi-column layouts.
  - **Scanned PDF**: Automatic OCR fallback (using Tesseract) if no text layer is found.
  - **DOCX**: Extract text, headers, and tables (preserving row/column structure).
  - **XLSX**: Extract data from all sheets, handle formulas (evaluate values), and ignore hidden sheets.
- [ ] **Table Extraction**: Identify and extract tables as structured JSON objects (not just flat text).
- [ ] **Metadata Extraction**: Capture filename, file size, creation date, page count, and author.
- [ ] **Batch Processing**: Ability to process a directory of files asynchronously.
- [ ] **Error Handling**: Graceful failure for corrupted files or password-protected documents (return specific error codes).

### Non-Functional
- [ ] **Performance**: Parse a 100-page PDF in < 5 seconds (text-only) or < 30 seconds (OCR).
- [ ] **Memory Efficiency**: Stream large files to avoid OOM errors (max file size 50MB).
- [ ] **Accuracy**: > 99% text extraction accuracy for digital documents.
- [ ] **Modularity**: Easy to add new parsers (e.g., PPTX) via a common interface.

## Input/Output Definitions

### Parser Interface (`src/parsers/base.py`)
```python
class BaseParser(ABC):
    @abstractmethod
    async def parse(self, file_path: Path) -> ParsedDocument:
        """Parses a file and returns a structured document object."""
        ...

class ParsedDocument(BaseModel):
    filename: str
    file_type: str
    metadata: Dict[str, Any]
    content: List[PageContent]

class PageContent(BaseModel):
    page_number: int
    text: str
    tables: List[Dict[str, Any]] = [] # List of structured tables
```

### Output JSON Example
```json
{
  "filename": "antrag_2024.pdf",
  "file_type": "pdf",
  "metadata": {
    "size_bytes": 204800,
    "created": "2024-01-15T10:00:00Z",
    "pages": 12
  },
  "content": [
    {
      "page_number": 1,
      "text": "Projektantrag IFB PROFI...",
      "tables": []
    },
    {
      "page_number": 3,
      "text": "Finanzplan Übersicht:",
      "tables": [
        {
          "headers": ["Position", "Betrag"],
          "rows": [["Personal", "50.000"], ["Sachmittel", "20.000"]]
        }
      ]
    }
  ]
}
```

## Test Cases

| ID | Name | Description | Expected Result |
|----|------|-------------|-----------------|
| TC-PAR-01 | **PDF Text Extraction** | Parse standard digital PDF | Text matches source, correct page count |
| TC-PAR-02 | **PDF OCR Fallback** | Parse image-only PDF | Text extracted via OCR, warning logged |
| TC-PAR-03 | **DOCX Table** | Parse Word doc with table | Table structure preserved in JSON |
| TC-PAR-04 | **XLSX Formulas** | Parse Excel with formulas | Evaluated values returned (not formulas) |
| TC-PAR-05 | **Corrupted File** | Parse truncated file | Raises `DocumentParsingError` |
| TC-PAR-06 | **Large File** | Parse 50MB PDF | Completes without memory crash |
| TC-PAR-07 | **Password Protected** | Parse encrypted PDF | Raises `PasswordProtectedError` |

## Success Criteria
- [ ] All 7 test cases pass.
- [ ] Unified interface handles all 3 file types transparently.
- [ ] OCR is functional (Tesseract installed and linked).
- [ ] Table data is structured enough for LLM interpretation.

## Dependencies
- `pymupdf` (PDF parsing)
- `pytesseract` (OCR)
- `python-docx` (Word parsing)
- `openpyxl` (Excel parsing)
- `pandas` (Data manipulation)

## Files to Create
- `src/parsers/base.py`
- `src/parsers/pdf_parser.py`
- `src/parsers/docx_parser.py`
- `src/parsers/xlsx_parser.py`
- `src/parsers/factory.py`
- `tests/test_parsers/test_pdf.py`
- `tests/test_parsers/test_docx.py`
- `tests/test_parsers/test_xlsx.py`
