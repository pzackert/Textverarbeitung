from pathlib import Path
import os

BASE_DIR = Path("/Users/patrick.zackert/Workspace/masterprojekt/option_2_platform")
DATA_DIR = BASE_DIR / "data"
INPUT_DIR = DATA_DIR / "input"
PROJECT_ID = "8209d44a"

base_path = INPUT_DIR / PROJECT_ID
uploads_dir = base_path / "uploads"
annotated_dir = base_path / "annotated"

print(f"Base Dir: {BASE_DIR}")
print(f"Uploads Dir: {uploads_dir} (Exists: {uploads_dir.exists()})")
print(f"Annotated Dir: {annotated_dir} (Exists: {annotated_dir.exists()})")

if uploads_dir.exists():
    for file_path in uploads_dir.iterdir():
        if file_path.name.startswith("."): continue
        
        print(f"\nProcessing: {file_path.name}")
        annotated_name = f"{file_path.stem}_annotated{file_path.suffix}"
        annotated_path = annotated_dir / annotated_name
        
        exists = annotated_path.exists()
        print(f"  Target Annotated Name: {annotated_name}")
        print(f"  Target Path: {annotated_path}")
        print(f"  EXISTS: {exists}")
        
        if not exists:
            # List directory to see what IS there
            print("  Directory contents:")
            for f in annotated_dir.iterdir():
                print(f"    - {f.name}")
