from abc import ABC, abstractmethod
from typing import List
from pathlib import Path
from .models import Document
from .exceptions import UnsupportedFormatError

class BaseParser(ABC):
    """Abstract base class for all document parsers"""
    
    supported_formats = []
    
    @abstractmethod
    def parse(self, file_path: str) -> List[Document]:
        """Parse a document and return list of Document objects"""
        pass
    
    def accepts_format(self, file_path: str) -> bool:
        """Check if parser can handle this file format"""
        ext = Path(file_path).suffix.lower().lstrip('.')
        return ext in self.supported_formats
    
    def validate_format(self, file_path: str) -> None:
        """Raise exception if format not supported"""
        if not self.accepts_format(file_path):
            raise UnsupportedFormatError(
                f"Format not supported: {Path(file_path).suffix}"
            )
