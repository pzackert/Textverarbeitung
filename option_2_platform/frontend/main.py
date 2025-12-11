from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from frontend.routers import dashboard, projects, benchmark, chat, settings, logo, admin

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
app.include_router(benchmark.router)
app.include_router(chat.router)
app.include_router(settings.router)
app.include_router(logo.router)
app.include_router(admin.router)

@app.get("/health")
async def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("frontend.main:app", host="0.0.0.0", port=8000, reload=True)
