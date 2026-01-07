import os
import shutil
from pathlib import Path

DATA_DIR = Path("/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input")

def normalize_projects():
    if not DATA_DIR.exists():
        return

    for project_dir in DATA_DIR.iterdir():
        if not project_dir.is_dir() or project_dir.name.startswith('.'):
            continue

        print(f"Processing {project_dir.name}...")
        
        uploads_dir = project_dir / "uploads"
        annotated_dir = project_dir / "annotated"
        
        uploads_dir.mkdir(exist_ok=True)
        annotated_dir.mkdir(exist_ok=True)
        
        # 1. Remove legacy input/output if empty
        legacy_input = project_dir / "input"
        legacy_output = project_dir / "output"
        
        if legacy_input.exists() and legacy_input.is_dir():
            try:
                legacy_input.rmdir()
                print("  Removed empty 'input' folder")
            except OSError:
                print("  'input' folder not empty, skipping removal")

        if legacy_output.exists() and legacy_output.is_dir():
            try:
                legacy_output.rmdir()
                print("  Removed empty 'output' folder")
            except OSError:
                print("  'output' folder not empty, skipping removal")

        # 2. Move root files to uploads (white-list exclusion)
        excluded = {
            "chat_history.json",
            "meta.json",
            "metadata.json",
            "criteria_responses.json",
            "uploads",
            "annotated",
            "input",
            "output",
        }
        
        for item in project_dir.iterdir():
            if item.name in excluded:
                continue
            
            if item.is_file():
                print(f"  Moving {item.name} to uploads/")
                shutil.move(str(item), str(uploads_dir / item.name))

if __name__ == "__main__":
    normalize_projects()
