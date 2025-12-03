# Parser Usage Guide

## Overview
The parser module provides standardized document extraction with a common interface.

## Installation

```bash
uv pip install pymupdf==1.26.6 python-docx==1.1.2 openpyxl==3.1.5
```

## Basic Usage

### Importing Parsers

```python
from src.parsers import Document, PDFParser, DocxParser, XlsxParser
from src.parsers import ParserError, CorruptedFileError
```

### PDF Parser

```python
parser = PDFParser()

# Parse PDF file
documents = parser.parse('document.pdf')

# Access content and metadata
for doc in documents:
    print(f"Page {doc.metadata['page_number']}: {len(doc.content)} chars")
    print(doc.content[:500])
```

**Output**: List of Document objects (one per page)

### DOCX Parser

```python
parser = DocxParser()

# Parse DOCX file
documents = parser.parse('document.docx')

# Access metadata
doc = documents[0]
print(f"Paragraphs: {doc.metadata['paragraph_count']}")
print(f"Tables: {doc.metadata['table_count']}")
print(doc.content)
```

**Output**: List with single Document object

### XLSX Parser

```python
parser = XlsxParser()

# Parse XLSX file (creates one Document per data row)
documents = parser.parse('data.xlsx')

# Each document is a row
for doc in documents:
    print(f"Sheet: {doc.metadata['sheet_name']}, Row: {doc.metadata['row_number']}")
    print(doc.content)
```

**Output**: List of Document objects (one per data row)

## Document Model

```python
@dataclass
class Document:
    content: str                    # Extracted text
    metadata: Dict[str, Any]        # Format-specific metadata
    source_file: str                # Original file path
    file_type: str                  # 'pdf', 'docx', or 'xlsx'
    
    @property
    def filename(self) -> str:      # Extract filename
    
    def to_dict(self) -> Dict:      # Convert to dictionary
```

## Error Handling

```python
from src.parsers import ParserError, CorruptedFileError, EmptyDocumentError

try:
    documents = parser.parse('document.pdf')
except FileNotFoundError:
    print("File not found")
except CorruptedFileError:
    print("File cannot be read")
except EmptyDocumentError:
    print("No text extracted")
except ParserError as e:
    print(f"Parsing error: {e}")
```

## Performance Notes

- PDF parsing: ~100-500ms depending on file size
- DOCX parsing: ~50-200ms
- XLSX parsing: ~50-100ms per sheet
- Memory usage: Minimal
