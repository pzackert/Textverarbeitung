import os
import json
import shutil
from typing import List, Dict, Optional
from datetime import datetime

PROJECTS_DIR = "data/projects"

class ProjectService:
    def __init__(self):
        os.makedirs(PROJECTS_DIR, exist_ok=True)

    def list_projects(self) -> List[Dict]:
        projects = []
        if not os.path.exists(PROJECTS_DIR):
            return []
            
        for dirname in os.listdir(PROJECTS_DIR):
            dirpath = os.path.join(PROJECTS_DIR, dirname)
            if os.path.isdir(dirpath):
                meta_path = os.path.join(dirpath, "metadata.json")
                if os.path.exists(meta_path):
                    with open(meta_path, "r") as f:
                        projects.append(json.load(f))
        return sorted(projects, key=lambda x: x.get("created_at", ""), reverse=True)

    def create_project(self, name: str, description: Optional[str] = None) -> Dict:
        project_id = name.lower().replace(" ", "-")
        project_dir = os.path.join(PROJECTS_DIR, project_id)
        os.makedirs(project_dir, exist_ok=True)
        
        project = {
            "id": project_id,
            "name": name,
            "description": description,
            "created_at": datetime.now().isoformat(),
            "documents": []
        }
        
        with open(os.path.join(project_dir, "metadata.json"), "w") as f:
            json.dump(project, f, indent=2)
            
        return project

    def get_project(self, project_id: str) -> Optional[Dict]:
        project_dir = os.path.join(PROJECTS_DIR, project_id)
        meta_path = os.path.join(project_dir, "metadata.json")
        if not os.path.exists(meta_path):
            return None
            
        with open(meta_path, "r") as f:
            return json.load(f)

    def save_document(self, project_id: str, filename: str, content: bytes) -> str:
        project_dir = os.path.join(PROJECTS_DIR, project_id)
        docs_dir = os.path.join(project_dir, "documents")
        os.makedirs(docs_dir, exist_ok=True)
        
        file_path = os.path.join(docs_dir, filename)
        with open(file_path, "wb") as f:
            f.write(content)
            
        # Update metadata
        project = self.get_project(project_id)
        if project:
            if "documents" not in project:
                project["documents"] = []
            if filename not in project["documents"]:
                project["documents"].append(filename)
            
            with open(os.path.join(project_dir, "metadata.json"), "w") as f:
                json.dump(project, f, indent=2)
                
        return file_path

project_service = ProjectService()
