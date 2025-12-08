import logging
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.gzip import GZipMiddleware
from pathlib import Path

from src.api.main import app as api_app
from frontend.routers import dashboard, projects, chat, admin

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

def create_app() -> FastAPI:
    app = FastAPI(title="IFB PROFI Platform")
    
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
    
    return app

app = create_app()
