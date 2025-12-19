import json
import uuid
import shutil
import logging
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime
from src.api.schemas_application import Application, ApplicationCreate, ApplicationUpdate, ApplicationDocument, ApplicationSummary

logger = logging.getLogger(__name__)

class ApplicationService:
    def __init__(self, base_path: str = "data/input"):
        self.base_path = Path(base_path)
        self.registry_file = self.base_path / "registry.json"
        
        # Ensure directories exist
        self.base_path.mkdir(parents=True, exist_ok=True)
        if not self.registry_file.exists():
            self._save_registry({})

    def _load_registry(self) -> Dict[str, dict]:
        try:
            with open(self.registry_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load registry: {e}")
            logger.error(f"Failed to load registry: {e}")
            return {}

    def _sync_with_disk(self):
        """Scan base_path for folders and add them to registry if missing."""
        registry = self._load_registry()
        changed = False
        
        # Iterate over directories in base_path
        if self.base_path.exists():
            for item in self.base_path.iterdir():
                if item.is_dir() and not item.name.startswith('.'):
                    app_id = item.name
                    # Skip if already invalid or output/annotated helper folders if they exist at root
                    if app_id in ["output", "annotated", "uploads"]: continue
                    
                    if app_id not in registry:
                        # Found unregistered app folder
                        logger.info(f"Discovered unregistered app: {app_id}")
                        
                        # Try to find some metadata or defaults
                        # Check for documents
                        docs = []
                        updated_at = datetime.utcnow()
                        
                        # Check input folder
                        input_dir = item / "input"
                        if not input_dir.exists():
                            # Maybe flat structure? User said data/input/8209d44a/uploads
                            # Let's check 'uploads' folder as seen in ls
                            input_dir = item / "uploads"
                        
                        if input_dir.exists():
                            for f in input_dir.iterdir():
                                if f.is_file() and not f.name.startswith('.'):
                                    docs.append(ApplicationDocument(
                                        filename=f.name,
                                        size_bytes=f.stat().st_size,
                                        content_type="application/pdf" if f.suffix == ".pdf" else "application/octet-stream",
                                        is_indexed=False, # Assume not indexed
                                        has_annotated_version=self._check_annotated_exists(app_id, f.name)
                                    ).dict())
                        
                        registry[app_id] = Application(
                            id=app_id,
                            title=f"Imported Application {app_id[:8]}", # Placeholder
                            applicant="Unknown Applicant",
                            status="analyzed", # Assume verified if existing
                            created_at=datetime.utcnow(),
                            updated_at=updated_at,
                            documents=docs
                        ).dict()
                        changed = True
        
        if changed:
            self._save_registry(registry)

    def _save_registry(self, data: Dict[str, dict]):
        with open(self.registry_file, 'w') as f:
            json.dump(data, f, indent=2, default=str)

    def list_applications(self) -> List[ApplicationSummary]:
        self._sync_with_disk()
        data = self._load_registry()
        # Sort by updated_at desc
        apps = data.values()
        sorted_apps = sorted(apps, key=lambda x: x.get('updated_at', ''), reverse=True)
        
        return [
            ApplicationSummary(
                id=a['id'],
                title=a['title'],
                applicant=a['applicant'],
                status=a['status'],
                created_at=a['created_at'],
                updated_at=a['updated_at'],
                document_count=len(a.get('documents', []))
            ) for a in sorted_apps
        ]

    def _check_annotated_exists(self, app_id: str, filename: str) -> bool:
        """Check if annotated version exists on disk."""
        try:
            name, ext = filename.rsplit('.', 1) if '.' in filename else (filename, "")
            annotated_name = f"{name}_annotated.{ext}"
            return (self.base_path / app_id / "annotated" / annotated_name).exists()
        except:
            return False

    def create_application(self, req: ApplicationCreate) -> Application:
        app_id = str(uuid.uuid4())
        now = datetime.utcnow()
        
        # Create Folder Structure
        app_dir = self.base_path / app_id
        (app_dir / "input").mkdir(parents=True, exist_ok=True)
        (app_dir / "output").mkdir(parents=True, exist_ok=True)
        
        new_app = Application(
            id=app_id,
            title=req.title,
            applicant=req.applicant,
            description=req.description,
            funding_request=req.funding_request,
            status="draft",
            created_at=now,
            updated_at=now,
            documents=[]
        )
        
        # Save to registry
        registry = self._load_registry()
        registry[app_id] = new_app.dict()
        self._save_registry(registry)
        
        return new_app

    def get_application(self, app_id: str) -> Optional[Application]:
        registry = self._load_registry()
        data = registry.get(app_id)
        if not data:
            return None
        
        # Check for annotated files dynamically
        app = Application(**data)
        base_dir = self.base_path / app_id / "annotated"
        if base_dir.exists():
            for doc in app.documents:
                name, ext = doc.filename.rsplit('.', 1) if '.' in doc.filename else (doc.filename, "")
                # Check pattern: filename_annotated.ext
                annotated_name = f"{name}_annotated.{ext}"
                doc.has_annotated_version = (base_dir / annotated_name).exists()
                
        return app

    def update_application(self, app_id: str, updates: ApplicationUpdate) -> Optional[Application]:
        registry = self._load_registry()
        if app_id not in registry:
            return None
            
        app_data = registry[app_id]
        
        # update fields
        update_dict = updates.dict(exclude_unset=True)
        for k, v in update_dict.items():
            app_data[k] = v
            
        app_data['updated_at'] = datetime.utcnow()
        
        registry[app_id] = app_data
        self._save_registry(registry)
        
        return Application(**app_data)

    def delete_application(self, app_id: str) -> bool:
        registry = self._load_registry()
        if app_id in registry:
            # Remove from registry
            del registry[app_id]
            self._save_registry(registry)
            
            # Remove folder
            app_dir = self.base_path / app_id
            if app_dir.exists():
                shutil.rmtree(app_dir, ignore_errors=True)
            return True
        return False

    def add_document(self, app_id: str, filename: str, content: bytes) -> Optional[ApplicationDocument]:
        registry = self._load_registry()
        if app_id not in registry:
            return None
            
        app_data = registry[app_id]
        
        # Save file
        file_path = self.base_path / app_id / "input" / filename
        with open(file_path, "wb") as f:
            f.write(content)
            
        # Create doc record
        doc = ApplicationDocument(
            filename=filename,
            size_bytes=len(content),
            content_type="application/pdf" if filename.endswith(".pdf") else "application/octet-stream",
            has_annotated_version=False
        )
        
        app_data.setdefault('documents', []).append(doc.dict())
        app_data['updated_at'] = datetime.utcnow()
        
        registry[app_id] = app_data
        self._save_registry(registry)
        
        return doc

    def mark_documents_indexed(self, app_id: str) -> None:
        """Mark all documents as indexed."""
        registry = self._load_registry()
        if app_id not in registry:
            return
            
        app_data = registry[app_id]
        if 'documents' in app_data:
            for doc in app_data['documents']:
                doc['is_indexed'] = True
        
        app_data['updated_at'] = datetime.utcnow()
        registry[app_id] = app_data
        self._save_registry(registry)

# Singleton
application_service = ApplicationService()
