#!/usr/bin/env python3
"""
Environment Cleanup Script.
Deletes virtual environments, logs, and cache files to allow a fresh install.
Key Persistent Data (data/) is PRESERVED.
"""
import shutil
import sys
from pathlib import Path

def clean_environment():
    root_dir = Path(__file__).parent.parent
    
    # Stop any uvicorn left behind
    import subprocess
    try:
        subprocess.run(["pkill", "-f", "uvicorn"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    # Paths to clean
    targets = [
        root_dir / ".venv",
        root_dir / "venv",
        root_dir / ".uv",
        root_dir / ".cache/uv",
        root_dir / "logs",
        root_dir / "coverage",
        root_dir / ".pytest_cache",
        root_dir / ".ruff_cache",
    ]
    
    print("🧹 Cleaning Environment...")
    print(f"Root: {root_dir}")
    
    cleaned_count = 0
    for target in targets:
        if target.exists():
            print(f"   Deleting: {target.name}...")
            if target.is_dir():
                shutil.rmtree(target)
            else:
                target.unlink()
            cleaned_count += 1
            
    # Clean __pycache__ recursively
    print("   Cleaning __pycache__ files...")
    for p in root_dir.rglob("__pycache__"):
        if p.is_dir():
            shutil.rmtree(p)

    print(f"\n✨ Cleanup Complete. ({cleaned_count} major items removed)")
    print("Next Steps:")
    print("1. uv venv")
    print("2. uv sync")
    print("3. uv run uvicorn src.api.main:app --reload --port 8000")
    print("   (run inside option_2_platform or use --directory option_2_platform from repo root)")

if __name__ == "__main__":
    clean_environment()
