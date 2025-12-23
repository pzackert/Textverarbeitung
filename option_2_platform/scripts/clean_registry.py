import json
import os
from pathlib import Path

DATA_DIR = Path("/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform/data/input")
REGISTRY_PATH = DATA_DIR / "registry.json"

def clean_registry():
    if not REGISTRY_PATH.exists():
        print("Registry not found.")
        return

    # Get actual folders
    actual_folders = {d.name for d in DATA_DIR.iterdir() if d.is_dir()}
    print(f"Found folders: {actual_folders}")

    with open(REGISTRY_PATH, 'r') as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            print("Invalid JSON in registry.")
            return

    # Filter projects
    new_data = {pid: p for pid, p in data.items() if pid in actual_folders}
    
    deleted_count = len(data) - len(new_data)
    print(f"Removing {deleted_count} deleted projects from registry.")

    with open(REGISTRY_PATH, 'w') as f:
        json.dump(new_data, f, indent=2, ensure_ascii=False)
    
    print("Registry cleaned.")

if __name__ == "__main__":
    clean_registry()
