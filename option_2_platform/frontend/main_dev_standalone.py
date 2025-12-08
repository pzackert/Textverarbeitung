"""
DEV ONLY STANDALONE ENTRY POINT
This file is for developing the frontend in isolation.
For the full application, use scripts/start_app.py
"""

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from frontend.routers import dashboard, projects

# Define base paths
BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="Textverarbeitung Platform")

# Mount static files
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Include Routers
app.include_router(dashboard.router)
app.include_router(projects.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("frontend.main:app", host="0.0.0.0", port=8000, reload=True)
