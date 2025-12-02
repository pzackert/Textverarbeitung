# Metadata Schemas

## PDF Metadata
```python
{
    "page_number": int,
    "total_pages": int,
    "file_size": int,       # bytes
    "created_date": str,    # ISO format if available
    "modified_date": str,   # ISO format if available
    "author": str,          # if available
    "title": str            # if available
}
```

## DOCX Metadata
```python
{
    "paragraph_count": int,
    "table_count": int,
    "file_size": int,       # bytes
    "modified_date": str,   # ISO format
    "author": str,
    "title": str,
    "last_modified_by": str
}
```

## XLSX Metadata
```python
{
    "sheet_name": str,
    "row_number": int,
    "column_headers": List[str],
    "file_size": int,       # bytes
    "modified_date": str    # ISO format
}
```
