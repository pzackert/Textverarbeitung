import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routers import ingest, query, system, criteria, knowledge, chat_global, projects
from src.api.routers import rag_global, chat_project, rag_project
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
app.include_router(ingest.router)
app.include_router(query.router)
app.include_router(system.router)
app.include_router(criteria.router)
app.include_router(criteria.eval_router)
app.include_router(knowledge.router)
app.include_router(chat_global.router)
app.include_router(chat_project.router)
app.include_router(rag_global.router)
app.include_router(rag_project.router)
app.include_router(projects.router)


@app.get("/")
async def root():
    return {
        "name": "IFB PROFI RAG API",
        "version": "1.0.0",
        "status": "running",
        "docs_url": "/docs"
    }
