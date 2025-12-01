import json
import shutil
from pathlib import Path
from typing import List, Optional
from src.core.models import Project, Document

class ProjectService:
    def __init__(self, storage_root: Path):
        self.storage_root = storage_root
        self.storage_root.mkdir(parents=True, exist_ok=True)

    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        project = Project(name=name, description=description)
        project_dir = self.storage_root / project.id
        project_dir.mkdir(parents=True, exist_ok=True)
        
        # Create documents folder
        (project_dir / "documents").mkdir(exist_ok=True)
        
        self._save_metadata(project)
        return project

    def list_projects(self) -> List[Project]:
        projects = []
        for project_dir in self.storage_root.iterdir():
            if project_dir.is_dir():
                metadata_file = project_dir / "metadata.json"
                if metadata_file.exists():
                    try:
                        with open(metadata_file, "r") as f:
                            data = json.load(f)
                            projects.append(Project(**data))
                    except Exception:
                        # Skip malformed projects
                        continue
        
        # Sort by created_at desc
        projects.sort(key=lambda p: p.created_at, reverse=True)
        return projects

    def get_project(self, project_id: str) -> Optional[Project]:
        metadata_file = self.storage_root / project_id / "metadata.json"
        if not metadata_file.exists():
            return None
        
        try:
            with open(metadata_file, "r") as f:
                data = json.load(f)
                return Project(**data)
        except Exception:
            return None

    def _save_metadata(self, project: Project):
        project_dir = self.storage_root / project.id
        metadata_file = project_dir / "metadata.json"
        with open(metadata_file, "w") as f:
            f.write(project.model_dump_json())

    def save_document(self, project_id: str, filename: str, content: bytes) -> Optional[Document]:
        project = self.get_project(project_id)
        if not project:
            return None
            
        doc = Document(filename=filename, path=f"documents/{filename}")
        
        # Save file
        file_path = self.storage_root / project_id / "documents" / filename
        with open(file_path, "wb") as f:
            f.write(content)
            
        # Update project metadata
        project.documents.append(doc)
        self._save_metadata(project)
        
        return doc
