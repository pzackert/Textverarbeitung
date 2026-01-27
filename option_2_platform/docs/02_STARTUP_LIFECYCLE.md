# Startup Lifecycle

The system implements a self-healing startup sequence to verify environment integrity before serving requests.

## Startup Sequence

1.  **Model Scanner**: Detects available models from the configured provider (Ollama/LM Studio).
2.  **AI Provider Check**: Verifies connectivity to the LLM backend (Port 11434 or 1234).
3.  **Vector Store Init**: Initializes the ChromaDB persistent client in `data/chromadb`.
4.  **LLM Loading**: Preloads the configured model context if supported.
5.  **Global Knowledge Ingest**: Indexes files found in `data/global_knowledge` if not already indexed.
6.  **Project Healing**: Scans `data/input/{id}` folders for missing artifacts and repairs them.

## Auto-Healing Capabilities

The backend ensures data consistency at startup:
-   **Folder Structure**: Automatically creates `uploads/` and `annotated/` directories within project folders if missing.
-   **Metadata**: Generates `metadata.json` for projects identified by directory name if the file is absent.
-   **Criteria**: Initializes `criteria_responses.json` with a pending state if missing.

## Shutdown & Restart

-   **Trigger**: A restart can be triggered via the UI (clicking the logo) or API:
    `GET /api/system/startup?restart=true`
-   **Graceful Shutdown**: The system attempts to close DB connections and finish active ingestion tasks before reloading.
-   **Note**: Using process kill (SIGKILL) is discouraged as it may corrupt the vector store.

## Degraded Mode

If the LLM provider is unreachable:
1.  The system starts in **Degraded Mode**.
2.  The Dashboard (`/projects`) loads normally.
3.  RAG features and Chat will display error states but do not crash the application.
4.  A red status indicator is shown in the UI.
