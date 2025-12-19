# Implementation Plan: Platform Core & Project Management

**Branch**: `main` | **Date**: 2025-11-26 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `specs/initial-setup/spec.md`

## Summary

Initialize the "Option 2 Platform" with a modular FastAPI architecture, HTMX-based frontend, and core Project Management capabilities (Create, List, Upload Documents).

## Technical Context

**Language/Version**: Python 3.10+
**Primary Dependencies**: FastAPI, Uvicorn, Jinja2, Python-Multipart, HTMX (via CDN or static), TailwindCSS (via CDN for MVP).
**Storage**: Local filesystem (JSON for metadata, folders for documents).
**Testing**: Pytest
**Target Platform**: Local execution (macOS/Linux/Windows).
**Project Type**: Web Application (Server-Side Rendered).

## Constitution Check

- [x] **Modular Architecture**: We will separate `core`, `frontend`, and `backend` (services).
- [x] **Local-First AI**: Setup prepares for local file handling, prerequisite for local RAG.
- [x] **Server-Driven UI**: Using Jinja2 + HTMX.
- [x] **Async by Default**: FastAPI endpoints will be `async def`.

## Implementation Phases

### Phase 1: Core Infrastructure
**Goal**: Get the server running with basic routing and static asset serving.
- [ ] Initialize `FastAPI` app in `backend/main.py` (or `frontend/main.py` if serving UI).
- [ ] Configure `StaticFiles` for CSS/JS.
- [ ] Setup `Jinja2Templates`.
- [ ] Create base layout template (`base.html`).

### Phase 2: Project Service (Backend)
**Goal**: Business logic for managing projects.
- [ ] Define `Project` data model (Pydantic).
- [ ] Implement `ProjectService` for CRUD operations (saving to `data/projects/`).
- [ ] Create API endpoints (or internal service calls) for creating/listing projects.

### Phase 3: Dashboard UI (Frontend)
**Goal**: User can view and create projects.
- [ ] Create `index.html` (Dashboard) template.
- [ ] Implement `/` route to render Dashboard with project list.
- [ ] Implement `POST /projects` route to handle form submission (HTMX).
- [ ] Add "New Project" modal/form.

### Phase 4: Project Detail & Upload
**Goal**: User can view project details and upload files.
- [ ] Create `project_detail.html` template.
- [ ] Implement `/projects/{id}` route.
- [ ] Implement `POST /projects/{id}/upload` route for file uploads.
- [ ] Update UI to list uploaded files.

## Tasks

See `tasks.md` (to be generated) for granular breakdown.
