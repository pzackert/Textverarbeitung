# Feature Specification: Platform Core & Project Management

**Feature Branch**: `main` (Initial Setup)
**Created**: 2025-11-26
**Status**: Active
**Input**: Initial Platform Setup

## User Scenarios & Testing

### User Story 1 - Project Management (Priority: P1)

As a user, I want to create and list analysis projects so that I can organize my work.

**Why this priority**: This is the foundational entity for the entire application. Without projects, we cannot store documents or results.

**Independent Test**: Can be tested by creating a project via the UI and verifying it appears in the list.

**Acceptance Scenarios**:
1. **Given** the dashboard, **When** I click "New Project" and enter a name, **Then** a new project is created and I am redirected to its detail page.
2. **Given** a list of projects, **When** I view the dashboard, **Then** I see all created projects with their creation dates.

---

### User Story 2 - Document Upload (Priority: P1)

As a user, I want to upload PDF and DOCX files to a project so that they can be analyzed.

**Why this priority**: Documents are the input data for the RAG system.

**Independent Test**: Can be tested by uploading a file to a project and verifying it appears in the project's file list.

**Acceptance Scenarios**:
1. **Given** a project detail page, **When** I select a PDF file and click "Upload", **Then** the file is saved to the backend and listed in the "Documents" section.
2. **Given** an invalid file type (e.g., .exe), **When** I try to upload, **Then** I see an error message.

---

### User Story 3 - Basic Analysis Trigger (Priority: P2)

As a user, I want to start an analysis for a project so that I can get insights.

**Why this priority**: This connects the data (documents) to the value (AI insights).

**Independent Test**: Can be tested by clicking "Start Analysis" and verifying that a result (even a mock one) is generated.

**Acceptance Scenarios**:
1. **Given** a project with documents, **When** I click "Analyze", **Then** a background task is started (or simulated) and the status changes to "Processing".
2. **Given** a completed analysis, **When** I view the project, **Then** I see the results displayed.

## Technical Implementation Plan

### Backend (FastAPI)
- [ ] `Project` model and CRUD operations (SQLite/JSON).
- [ ] File upload endpoint handling `multipart/form-data`.
- [ ] Background task integration (using `BackgroundTasks` or simple async for MVP).

### Frontend (HTMX + Jinja2)
- [ ] Dashboard template with "New Project" modal/form.
- [ ] Project Detail template with "Upload" area.
- [ ] HTMX attributes for seamless updates without full page reloads.

### Storage
- [ ] Local file system storage for uploaded documents (`data/projects/{id}/documents`).
- [ ] Metadata storage (`data/projects/{id}/metadata.json`).
