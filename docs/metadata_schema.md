# Metadata Schemas

## PDF Metadata
```json
{
  "page_number": "int",
  "total_pages": "int",
  "file_size": "int (bytes)",
  "created_date": "str (ISO 8601)",
  "modified_date": "str (ISO 8601)",
  "author": "str",
  "title": "str"
}
```

## DOCX Metadata
```json
{
  "paragraph_count": "int",
  "table_count": "int",
  "file_size": "int (bytes)",
  "modified_date": "str (ISO 8601)",
  "author": "str",
  "title": "str",
  "last_modified_by": "str"
}
```

## XLSX Metadata
```json
{
  "sheet_name": "str",
  "row_number": "int",
  "column_headers": "List[str]",
  "file_size": "int (bytes)",
  "modified_date": "str (ISO 8601)"
}
```
