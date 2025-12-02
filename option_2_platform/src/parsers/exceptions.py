class ParserError(Exception):
    """Base exception for parsing errors"""
    pass

class UnsupportedFormatError(ParserError):
    """Raised when file format is not supported"""
    pass

class CorruptedFileError(ParserError):
    """Raised when file cannot be read or is corrupted"""
    pass

class EmptyDocumentError(ParserError):
    """Raised when no text can be extracted from document"""
    pass
