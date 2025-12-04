import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import ingest, query, system
from src.api.middleware import LoggingMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

app = FastAPI(
    title="IFB PROFI RAG API",
    version="1.0.0",
    description="REST API for IFB document analysis"
)

# Middleware
app.add_middleware(LoggingMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(ingest.router, prefix="/api/v1")
app.include_router(query.router, prefix="/api/v1")
app.include_router(system.router, prefix="/api/v1")

@app.get("/")
async def root():
    return {
        "name": "IFB PROFI RAG API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs"
    }
