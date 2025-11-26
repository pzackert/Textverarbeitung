# Tasks: Platform Core & Project Management

**Spec**: [spec.md](./spec.md) | **Plan**: [plan.md](./plan.md)

## Phase 1: Core Infrastructure
- [x] **Setup FastAPI App**: Create `frontend/main.py` as the entry point. Configure `FastAPI`, `StaticFiles` (mounting `frontend/static`), and `Jinja2Templates` (pointing to `frontend/templates`). <!-- id: 1 -->
- [x] **Base Template**: Create `frontend/templates/base.html` with HTML5 boilerplate, TailwindCSS CDN link, and HTMX CDN link. Define blocks for `content` and `scripts`. <!-- id: 2 -->
- [x] **Start Script**: Update `start_v2.sh` to run the new `frontend/main.py` with `uvicorn`. <!-- id: 3 -->

## Phase 2: Project Service (Backend)
- [x] **Data Models**: Create `backend/core/models.py` defining `Project` (id, name, description, created_at) and `Document` (id, filename, path) using Pydantic. <!-- id: 4 -->
- [x] **Project Service**: Create `backend/services/project_service.py`. Implement methods: `create_project`, `list_projects`, `get_project`, `save_document`. Use `data/projects` as storage root. <!-- id: 5 -->
- [x] **Dependency Injection**: Setup a `get_project_service` dependency in `backend/dependencies.py` (or similar) to provide the service instance. <!-- id: 6 -->

## Phase 3: Dashboard UI
- [ ] **Dashboard Route**: In `frontend/routers/dashboard.py`, create a route `GET /` that fetches projects via `ProjectService` and renders `index.html`. <!-- id: 7 -->
- [ ] **Dashboard Template**: Create `frontend/templates/index.html` extending `base.html`. Display a list of projects (or "No projects found"). <!-- id: 8 -->
- [ ] **Create Project Endpoint**: Create `POST /projects` in `frontend/routers/projects.py`. Handle form data, call `ProjectService.create_project`, and return an HTMX snippet (e.g., the new project row or full list) or redirect. <!-- id: 9 -->
- [ ] **New Project Form**: Add a simple form to `index.html` (or a modal) to submit to `POST /projects`. <!-- id: 10 -->

## Phase 4: Project Detail & Upload
- [ ] **Project Detail Route**: Create `GET /projects/{project_id}` in `frontend/routers/projects.py`. Fetch project details and render `project_detail.html`. <!-- id: 11 -->
- [ ] **Project Detail Template**: Create `frontend/templates/project_detail.html`. Show project info and a list of documents. <!-- id: 12 -->
- [ ] **Upload Endpoint**: Create `POST /projects/{project_id}/upload`. Handle `UploadFile`, save it using `ProjectService`, and return the updated document list HTML. <!-- id: 13 -->
- [ ] **Upload UI**: Add an `<input type="file">` form to `project_detail.html` with `hx-post` to the upload endpoint. <!-- id: 14 -->
