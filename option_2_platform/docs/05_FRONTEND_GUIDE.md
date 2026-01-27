# Frontend Guide

The frontend is a server-side rendered application with dynamic enhancements.

## Tech Stack
-   **Base**: Jinja2 Templates (Server-Side Rendering)
-   **Interactivity**: HTMX (Partial updates, AJAX)
-   **Logic**: Alpine.js (Client-side state, visibility toggles)
-   **Styling**: TailwindCSS
-   **PDF**: Mozilla PDF.js

## State Management

1.  **System Status**: The header polls `/api/system/status` every 5 seconds to update the "System Ready/Degraded" indicator.
2.  **Loading States**: HTMX indicators (`hx-indicator`) show spinners during server requests.
3.  **Chat**: `chat.js` manages the chat window, appending messages via DOM manipulation and persisting history via the Backend API.

## Layouts

-   **Dashboard**: Grid view of projects.
-   **Review Cockpit**: 3-Column Layout:
    1.  **File Sidebar**: List of project documents. Controlled by `ReviewState`.
    2.  **Document Viewer**: Central PDF/Text viewer. Supports "Original" and "Annotated" modes.
    3.  **Assistant/Criteria**: Right panel.
        -   **Chat**: Interactive Q&A.
        -   **Catalog**: Validation criteria list with status (Green/Red/Yellow).

## Review Logic
-   **Deep Linking**: Citations in Chat or Criteria Evidence can trigger the Viewer to jump to a specific page.
    -   Function: `window.renderDocument(filename, pageNumber)`
-   **Criteria Check**: Triggering a check sets a card to "loading", calls the Queue API, polls for completion, then swaps the card content with the result.
