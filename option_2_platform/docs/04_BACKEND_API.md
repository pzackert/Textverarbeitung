# Backend API

The API is built with **FastAPI**.

## Core Endpoints

### System
-   `GET /api/system/status`: Returns system health, LLM status, and disk usage. Used for UI polling.
-   `GET /api/system/startup`: Triggers system initialization. Accepts `?restart=true` to force reload.

### Projects
-   `GET /api/projects`: Lists all projects found in `data/input`.
-   `POST /api/projects`: Creates a new project.
-   `GET /api/projects/{id}/documents`: Returns metadata files for a specific project.
-   `POST /api/projects/{id}/upload`: Handles file uploads.

### Search & RAG
-   `POST /api/rag/query`: General RAG query.
-   `POST /api/chats/project/{id}/message`: Sends a chat message for a project context. Returns citations.

### Queue System (Criteria Validation)
-   `POST /api/queue/projects/{id}/criteria/{criterion_id}`: Enqueues a validation job for a specific criterion.
-   `GET /api/queue/{job_id}`: Poll status of a generic job (`pending`, `processing`, `completed`, `failed`).
-   **Polling Strategy**: The frontend should poll the job ID until completion, then fetch the updated project results.

## Settings API

-   `GET /api/settings`: Retrieves current configuration.
-   `POST /api/settings/llm`: Updates Model, Provider, Temperature.
-   `POST /api/settings/prompts`: Updates system prompts.
-   **Note**: Settings changes typically trigger a "Restart Required" flag.
