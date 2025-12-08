import shutil
import uuid
from pathlib import Path
from src.services.project_service import project_service

def setup_real_documents():
    # Source documents
    test_docs_dir = Path("data/test_documents")
    if not test_docs_dir.exists():
        print("Test documents directory not found!")
        return

    # Create a new project for Real Documents
    project_name = "Real Test Documents"
    
    # Check if project already exists
    projects = project_service.list_projects()
    existing_project = next((p for p in projects if p.name == project_name), None)
    
    if existing_project:
        print(f"Project '{project_name}' already exists. ID: {existing_project.id}")
        project = existing_project
    else:
        print(f"Creating project '{project_name}'...")
        project = project_service.create_project(
            name=project_name,
            description="Project with real test documents from Option 1",
            applicant="Smart Port Analytics GmbH",
            funding_amount=150000.0
        )
        print(f"Created project. ID: {project.id}")

    # Ensure project documents directory exists
    project_docs_dir = Path(f"data/projects/{project.id}/documents")
    project_docs_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy files and register them
    files_to_copy = [
        "IFB_Foerderantrag_Smart_Port_Analytics.pdf",
        "Projektskizze_Smart_Port_Analytics.docx",
        "Businessplan_Smart_Port_Analytics.xlsx"
    ]
    
    for filename in files_to_copy:
        src_file = test_docs_dir / filename
        if src_file.exists():
            dst_file = project_docs_dir / filename
            shutil.copy2(src_file, dst_file)
            print(f"Copied {filename} to project.")
            
            # Register document in project service (if not already there)
            # Note: project_service.add_document usually handles upload, 
            # here we manually add it to the project object if needed.
            # But let's use the service method to be safe if possible, 
            # or just manually update the JSON since we are in a script.
            
            # Check if doc already in project
            if not any(d.filename == filename for d in project.documents):
                from src.core.models import Document
                new_doc = Document(
                    filename=filename,
                    path=str(dst_file)
                )
                project.documents.append(new_doc)
                print(f"Registered {filename} in project metadata.")
        else:
            print(f"Warning: {filename} not found in test_documents.")
            
    # Save project
    project_service._save_projects({project.id: project}) # Accessing internal method for quick save
    print("Setup complete.")

if __name__ == "__main__":
    setup_real_documents()
