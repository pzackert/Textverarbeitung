import fitz
from pathlib import Path
from datetime import datetime
from typing import List

from .base import BaseParser
from .models import Document
from .exceptions import CorruptedFileError, EmptyDocumentError

class PDFParser(BaseParser):
    supported_formats = ['pdf']
    
    def parse(self, file_path: str) -> List[Document]:
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        try:
            doc = fitz.open(file_path)
        except Exception as e:
            raise CorruptedFileError(f"Cannot open PDF: {str(e)}")
        
        documents = []
        total_pages = len(doc)
        file_size = path.stat().st_size
        
        for page_num in range(total_pages):
            try:
                page = doc[page_num]
                text = page.get_text()
                
                if not text.strip():
                    continue
                
                metadata = {
                    "page_number": page_num + 1,
                    "total_pages": total_pages,
                    "file_size": file_size,
                    "created_date": datetime.now().isoformat(),
                    "modified_date": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
                }
                
                documents.append(Document(
                    content=text,
                    metadata=metadata,
                    source_file=str(file_path),
                    file_type="pdf"
                ))
            except Exception as e:
                raise CorruptedFileError(f"Error reading page {page_num + 1}: {str(e)}")
        
        doc.close()
        
        if not documents:
            raise EmptyDocumentError("No text extracted from PDF")
        
        return documents
