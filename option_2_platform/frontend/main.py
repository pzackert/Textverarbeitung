from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path

from frontend.routers import dashboard, projects, criteria, wizard

app = FastAPI(title="IFB Antragsprüfung")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend/templates")

# Include Routers
app.include_router(dashboard.router)
app.include_router(projects.router)
app.include_router(criteria.router)
app.include_router(wizard.router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("frontend.main:app", host="0.0.0.0", port=8000, reload=True)
