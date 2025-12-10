import json
import uuid
import os
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
    
    def create_project(self, name: str, description: Optional[str] = None, applicant: Optional[str] = None, funding_amount: Optional[float] = None) -> Project:
        """Create new project and persist."""
        projects = self._load_projects()
        project = Project(
            name=name,
            description=description,
            applicant=applicant,
            funding_amount=funding_amount
        )
        projects[project.id] = project
        self._save_projects(projects)
        return project
    
    def update_project_status(self, project_id: str, status: str) -> Optional[Project]:
        """Update project status."""
        projects = self._load_projects()
        project = projects.get(project_id)
        if not project:
            return None
            
        project.status = status
        project.updated_at = datetime.now()
        projects[project_id] = project
        self._save_projects(projects)
        return project

    def delete_project(self, project_id: str) -> bool:
        """Delete a project."""
        projects = self._load_projects()
        if project_id in projects:
            del projects[project_id]
            self._save_projects(projects)
            return True
        return False

    def list_projects(self) -> List[Project]:
        """List all projects."""
        projects = self._load_projects()
        # Sort by created_at desc
        return sorted(projects.values(), key=lambda p: p.created_at, reverse=True)

    def _validate_documents(self, project: Project) -> Project:
        """Validate existence of documents and update sizes."""
        valid_docs = []
        changed = False
        
        for doc in project.documents:
            # Check existence
            if os.path.exists(doc.path):
                # Update size if missing or zero
                try:
                    actual_size = os.path.getsize(doc.path)
                    if doc.size != actual_size:
                        doc.size = actual_size
                        changed = True
                    valid_docs.append(doc)
                except OSError:
                    changed = True # Skip if error accessing
            else:
                # Check legacy/alternative paths if not found
                # Or just mark as changed to remove it
                changed = True
                
        if changed:
            project.documents = valid_docs
            project.doc_count = len(valid_docs)
            # We don't save immediately to avoid IO spam, but we return the cleaned project
            # Optionally we could self.update_project(project) here if we want persistence of the cleanup
            # Let's save it to keep DB clean
            self.update_project(project)
            
        return project

    def get_project(self, project_id: str) -> Optional[Project]:
        projects = self._load_projects()
        project = projects.get(project_id)
        if project:
            return self._validate_documents(project)
        return None

    def save_document(self, project_id: str, filename: str, content: bytes) -> Optional[Document]:
        projects = self._load_projects()
        project = projects.get(project_id)
        if not project:
            return None
            
        # Save file physically
        # User requested path: data/input/<project_id>
        project_dir = Path("data/input") / project_id
        project_dir.mkdir(parents=True, exist_ok=True)
        file_path = project_dir / filename
        
        with open(file_path, "wb") as f:
            f.write(content)
            
        doc = Document(
            filename=filename, 
            path=str(file_path),
            size=len(content)
        )
        project.documents.append(doc)
        project.doc_count = len(project.documents) # Update count
        project.updated_at = datetime.now()
        
        projects[project_id] = project
        self._save_projects(projects)
        
        return doc

    def update_project(self, project: Project) -> None:
        """Update an existing project."""
        projects = self._load_projects()
        projects[project.id] = project
        self._save_projects(projects)

# Singleton instance
project_service = ProjectService()
