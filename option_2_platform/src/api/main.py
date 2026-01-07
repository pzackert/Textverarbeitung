import logging # Reload Trigger
import os
import sys
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers.ingest import router as ingest_router
from src.api.routers.query import router as query_router
from src.api.routers.system import router as system_router
from src.api.routers.criteria import router as criteria_router, eval_router as criteria_eval_router
from src.api.routers.knowledge import router as knowledge_router
from src.api.routers.chat_global import router as chat_global_router
from src.api.routers.projects import router as projects_router
from src.api.routers.rag_global import router as rag_global_router
from src.api.routers.chat_project import router as chat_project_router
from src.api.routers.rag_project import router as rag_project_router
from src.api.routers.settings import router as settings_router
from src.api.routers.queue import router as queue_router
from src.api.middleware import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@asynccontextmanager
async def lifespan(app_instance: FastAPI):
    """Startup and shutdown logic."""
    # Startup: Auto-load global knowledge if available
    if not (os.getenv("PYTEST_CURRENT_TEST") or "pytest" in sys.modules):
        # Load global knowledge in background thread to not block startup
        import threading
        from src.api.routers.rag_global import _reset_job, _clean_global_chunks, _run_load_job
        from src.api.dependencies import get_ingestion_pipeline
        
        def load_global_knowledge():
            try:
                data_dir = Path(__file__).parent.parent.parent / "data" / "global_knowledge"
                if data_dir.exists():
                    doc_paths = sorted([p for p in data_dir.iterdir() if p.is_file()])
                    if doc_paths:
                        logging.info("Auto-loading global knowledge base in background...")
                        _reset_job(doc_paths)
                        pipeline = get_ingestion_pipeline()
                        _clean_global_chunks()
                        _run_load_job(doc_paths, pipeline)
                        logging.info("✅ Global knowledge base preloaded successfully.")
                    else:
                        logging.warning("⚠️ Global knowledge directory empty. Add documents via /settings.")
                else:
                    logging.warning("⚠️ Global knowledge directory missing. Create data/global_knowledge/.")
            except Exception as exc:
                logging.error(f"❌ Failed to preload global knowledge: {exc}")
        
        thread = threading.Thread(target=load_global_knowledge, daemon=True)
        thread.start()
    
    yield
    # Shutdown logic (if needed)

app = FastAPI(
    title="IFB PROFI RAG API",
    version="1.0.0",
    description="REST API for IFB document analysis",
    lifespan=lifespan
)

# Startup Event
from src.services.system_state import run_startup_sequence
import asyncio

@app.on_event("startup")
async def startup_event():
    # Trigger background startup sequence
    asyncio.create_task(run_startup_sequence())

# Middleware
from src.api.middleware import StartupBlockingMiddleware
app.add_middleware(StartupBlockingMiddleware)
app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
# --- Backend API (Namespaced to /api to avoid conflict with Frontend) ---
app.include_router(ingest_router, prefix="/api")
app.include_router(query_router, prefix="/api")
app.include_router(system_router, prefix="/api")
app.include_router(criteria_router, prefix="/api")
app.include_router(criteria_eval_router, prefix="/api")
app.include_router(knowledge_router, prefix="/api")
app.include_router(chat_global_router, prefix="/api")
app.include_router(chat_project_router, prefix="/api")
app.include_router(rag_global_router, prefix="/api")
app.include_router(rag_project_router, prefix="/api")
app.include_router(projects_router, prefix="/api")
app.include_router(settings_router, prefix="/api")
app.include_router(queue_router, prefix="/api")

# --- Frontend Integration ---
from fastapi.staticfiles import StaticFiles
from frontend.routers import (
    projects as frontend_projects,
    chat as frontend_chat,
    settings as frontend_settings,
    criteria as frontend_criteria,
    dashboard as frontend_dashboard,
    admin as frontend_admin,
    benchmark as frontend_benchmark,
    logo as frontend_logo
)

# Mount Static Files
import os
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../frontend/static"))
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    logging.warning(f"Static directory not found at {static_dir}")

# Mount Frontend Routes
# Note: Ensure dashboard (root) is included last or check its specific paths to avoid conflicts if it catches-all.
# Based on inspection, dashboard likely handles root "/".
app.include_router(frontend_dashboard.router)  # Handles / (Dashboard)
app.include_router(frontend_projects.router)   # Handles /projects
app.include_router(frontend_chat.router)       # Handles /chat
app.include_router(frontend_settings.router)   # Handles /settings
app.include_router(frontend_criteria.router)   # Handles /criteria
app.include_router(frontend_admin.router)      # Handles /admin
app.include_router(frontend_benchmark.router)  # Handles /benchmark
app.include_router(frontend_logo.router)       # Handles /logo


# @app.get("/")
# async def root():
#     return {
#         "name": "IFB PROFI RAG API",
#         "version": "1.0.0",
#         "status": "running",
#         "docs_url": "/docs"
#     }
