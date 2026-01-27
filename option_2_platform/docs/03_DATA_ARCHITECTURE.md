# Data Architecture

The platform follows a **Local-First** principle. All data resides within the project directory to ensure isolation and portability.

## Directory Structure

```text
option_2_platform/
├── data/
│   ├── config/             # User settings (settings.json)
│   ├── chromadb/           # Vector Database (ChromaDB persistence)
│   ├── global_knowledge/   # Shared regulatory documents
│   └── input/              # Project Data
│       ├── {id}/           # Unique Project ID (e.g., 8209d44a)
│       │   ├── uploads/    # Raw uploaded files (PDF, DOCX)
│       │   ├── annotated/  # Processed/Annotated PDFs
│       │   ├── metadata.json           # Project metadata
│       │   ├── criteria_responses.json # Validation results
│       │   └── chat_history.json       # Chat persistence
```

## Project Isolation

-   **Folder-Based**: Each project is contained entirely within its `{id}` folder.
-   **No Central Registry**: The system scans `data/input/` directories to discover projects. Removing a folder permanently deletes the project.
-   **RAG Isolation**:
    -   When entering a project, the Vector Store enforces a filter: `metadata={"project_id": "{id}"}`.
    -   Before ingestion, existing chunks for the project are purged to prevent ghosting or data leakage between projects.

## Persistence

-   **Vector Store**: Uses ChromaDB in persistent mode.
-   **Chat**: History is saved to `chat_history.json`.
-   **Criteria**: Validation results are persisted in `criteria_responses.json`.
-   **Config**: `config/config.yaml` manages system-wide defaults; `data/config/settings.json` stores runtime overrides.
