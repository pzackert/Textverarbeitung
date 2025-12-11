import os
import json
import asyncio
from pathlib import Path
from typing import List, Dict, Any
from fastapi import APIRouter, Request, BackgroundTasks, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse

router = APIRouter(prefix="/benchmark", tags=["benchmark"])
# Robust relative path for templates
BASE_FRONTEND = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

# Path to benchmark results
# Root is ../../../ from this file
BASE_PROJECT = Path(__file__).resolve().parent.parent.parent
RESULTS_DIR = BASE_PROJECT / "tests" / "test_benchmarks" / "results"

@router.get("/")
async def benchmark_page(request: Request):
    """Renders the benchmark visualization page."""
    return templates.TemplateResponse(
        request=request,
        name="benchmark.html",
        context={"request": request, "current_page": "benchmark"}
    )

@router.get("/api/list")
async def list_benchmark_results():
    """Returns a list of available benchmark result files."""
    if not RESULTS_DIR.exists():
        return []

    files = []
    for f in RESULTS_DIR.glob("*.json"):
        files.append({
            "filename": f.name,
            "modified": f.stat().st_mtime
        })
    
    # Sort by modification time, newest first
    files.sort(key=lambda x: x["modified"], reverse=True)
    return [f["filename"] for f in files]

@router.get("/api/data/{filename}")
async def get_benchmark_data(filename: str):
    """Returns the content of a specific benchmark JSON file."""
    file_path = RESULTS_DIR / filename
    
    # Security check to prevent path traversal
    if not file_path.is_relative_to(RESULTS_DIR):
        raise HTTPException(status_code=400, detail="Invalid filename")
        
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
        
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def run_benchmark_task():
    """Background task to run the benchmark."""
    # This is a placeholder for the actual command.
    # We would run `uv run pytest tests/test_benchmarks/ ...`
    # For now, we simulate a delay.
    print("Starting background benchmark task...")
    
    # Construct the command
    # We use the full path to ensure it runs correctly
    cmd = "uv run pytest tests/test_benchmarks/test_benchmark_runner.py"
    
    try:
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(BASE_DIR)
        )
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print("Benchmark finished successfully.")
        else:
            print(f"Benchmark failed: {stderr.decode()}")
            
    except Exception as e:
        print(f"Error running benchmark: {e}")

@router.post("/api/run")
async def run_benchmark(background_tasks: BackgroundTasks):
    """Triggers the benchmark test in the background."""
    background_tasks.add_task(run_benchmark_task)
    return {"status": "started", "message": "Benchmark started in background."}
