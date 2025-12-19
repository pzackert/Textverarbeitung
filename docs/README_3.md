# Sample Data for IFB PROFI Platform

This directory contains generated sample data for testing the IFB PROFI Platform.

## Structure

- `applications/`: Contains generated funding applications. Each application has its own folder with:
    - `antrag.pdf`: The main application form.
    - `projektbeschreibung.docx`: Detailed project description.
    - `metadata.json`: Structured data about the application.
- `criteria/`: Contains the criteria catalog (`ifb_profi_criteria.json`).

## Generation

To generate the sample data, run:

```bash
python scripts/generate_sample_data.py
```

This script uses `reportlab` and `python-docx` to create realistic documents based on predefined templates and data models.

## Ingestion

To ingest the sample data into the Vector Database (ChromaDB), run:

```bash
python scripts/ingest_samples.py
```

This will parse the documents, chunk them, generate embeddings, and store them in ChromaDB.

## Usage in UI

You can also trigger generation and ingestion directly from the Dashboard using the "Load Sample Data" button in the Admin Actions section.
