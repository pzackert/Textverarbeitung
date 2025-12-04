import json
import uuid
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from src.core.models import Project, Document

class ProjectService:
    def __init__(self):
        self.storage_path = Path("data/projects/projects.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
    def _load_projects(self) -> Dict[str, Project]:
        """Load all projects from JSON file."""
        if not self.storage_path.exists():
            return {}
        with open(self.storage_path) as f:
            try:
                data = json.load(f)
                return {pid: Project(**pdata) for pid, pdata in data.items()}
            except json.JSONDecodeError:
                return {}
    
    def _save_projects(self, projects: Dict[str, Project]):
        """Save all projects to JSON file."""
        with open(self.storage_path, 'w') as f:
            # Use model_dump for Pydantic v2
            data = {pid: p.model_dump(mode='json') for pid, p in projects.items()}
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create_project(self, name: str, description: Optional[str] = None) -> Project:
        """Create new project and persist."""
        projects = self._load_projects()
        project = Project(
            name=name,
            description=description
        )
        projects[project.id] = project
        self._save_projects(projects)
        return project
    
    def list_projects(self) -> List[Project]:
        """List all projects."""
        projects = self._load_projects()
        # Sort by created_at desc
        return sorted(projects.values(), key=lambda p: p.created_at, reverse=True)

    def get_project(self, project_id: str) -> Optional[Project]:
        projects = self._load_projects()
        return projects.get(project_id)

    def save_document(self, project_id: str, filename: str, content: bytes) -> Optional[Document]:
        projects = self._load_projects()
        project = projects.get(project_id)
        if not project:
            return None
            
        # Save file physically
        project_dir = self.storage_path.parent / project_id / "documents"
        project_dir.mkdir(parents=True, exist_ok=True)
        file_path = project_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(content)
            
        doc = Document(filename=filename, path=str(file_path))
        project.documents.append(doc)
        
        projects[project_id] = project
        self._save_projects(projects)
        
        return doc

# Singleton instance
project_service = ProjectService()
