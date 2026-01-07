import logging
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pathlib import Path

from src.api.main import app as api_app
from frontend.routers import dashboard, projects, chat, admin, settings, logo
from src.api.routers import rag_global
from src.api.dependencies import get_ingestion_pipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def create_app() -> FastAPI:
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        # Preload global knowledge when available (skip during tests)
        if not (os.getenv("PYTEST_CURRENT_TEST") or "pytest" in sys.modules):
            data_dir = Path("data/global_knowledge")
            if data_dir.exists():
                doc_paths = sorted([p for p in data_dir.iterdir() if p.is_file()])
                if doc_paths:
                    try:
                        rag_global._reset_job(doc_paths)
                        pipeline = get_ingestion_pipeline()
                        rag_global._clean_global_chunks()
                        rag_global._run_load_job(doc_paths, pipeline)
                        logging.info("Global knowledge preloaded on startup.")
                    except Exception as exc:  # pragma: no cover
                        logging.error(f"Failed to preload global knowledge: {exc}")
                else:
                    logging.warning("Global knowledge directory empty; global chat will be unavailable until documents are added.")
            else:
                logging.warning("Global knowledge directory missing; global chat will be unavailable until loaded.")
        yield

    app = FastAPI(title="IFB PROFI Platform", lifespan=lifespan)
    
    # Enable GZip Compression
    app.add_middleware(GZipMiddleware, minimum_size=1000)
    
    # Mount API
    app.mount("/api/v1", api_app)
    
    # Mount Static Files
    # Assuming running from root of option_2_platform
    static_dir = Path("frontend/static")
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")
    
    # Cache Headers Middleware
    @app.middleware("http")
    async def add_cache_headers(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/static"):
            response.headers["Cache-Control"] = "public, max-age=86400"
        return response
    
    # Include Frontend Routers
    app.include_router(dashboard.router)
    app.include_router(projects.router)
    app.include_router(chat.router)
    app.include_router(admin.router)
    app.include_router(settings.router)
    app.include_router(logo.router)
    from frontend.routers import benchmark
    app.include_router(benchmark.router)

    return app

app = create_app()
