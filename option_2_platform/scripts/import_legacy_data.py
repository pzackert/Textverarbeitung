import shutil
import os
from pathlib import Path
import logging
from src.services.application_service import application_service
from src.api.schemas_application import ApplicationCreate

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

INPUT_DIR = Path("data/input")

def import_legacy_data():
    if not INPUT_DIR.exists():
        logger.error(f"Input directory {INPUT_DIR} does not exist.")
        return

    for item in INPUT_DIR.iterdir():
        if item.is_dir() and item.name not in [".DS_Store"]:
            app_id = item.name
            logger.info(f"Processing folder: {app_id}")

            # Check if app exists
            existing_app = application_service.get_application(app_id)
            
            if existing_app:
                logger.info(f"Application {app_id} already exists. Skipping creation.")
                target_app = existing_app
            else:
                # Create rudimentary app
                logger.info(f"Creating new app for {app_id}")
                # Try to guess title from documents or folders? 
                # For now, use ID as title
                create_req = ApplicationCreate(
                    title=f"Imported Application {app_id}",
                    applicant="Unknown Applicant",
                    description="Imported from data/input",
                    funding_request=0
                )
                # Create via service creates a NEW ID. We need to Force the ID.
                # Service doesn't support forcing ID in create_application.
                # We must manually inject it or hack the service.
                # Let's verify if we can misuse the service or if we should manually manipulate the registry.
                
                # Manual registry manipulation to preserve ID
                now = application_service._load_registry() # existing
                # Actually, duplicate the create logic but with fixed ID
                import datetime
                import uuid
                from src.api.schemas_application import Application
                
                # We need to manually construct the Application object and save it
                # Mimic create_application but with specific ID
                
                new_app = Application(
                    id=app_id,
                    title=f"Imported Application {app_id}",
                    applicant="Unknown Applicant",
                    description="Imported from data/input",
                    funding_request=0,
                    status="draft",
                    created_at=datetime.datetime.utcnow(),
                    updated_at=datetime.datetime.utcnow(),
                    documents=[]
                )
                
                # Ensure directory structure
                # The service uses data/applications/{id}
                app_dir = application_service.base_path / app_id
                app_dir.mkdir(parents=True, exist_ok=True)
                (app_dir / "input").mkdir(parents=True, exist_ok=True)
                (app_dir / "output").mkdir(parents=True, exist_ok=True)
                
                # Save to registry
                registry = application_service._load_registry()
                registry[app_id] = new_app.dict()
                application_service._save_registry(registry)
                logger.info(f"Registered app {app_id}")

            # Process Files (Uploads)
            uploads_dir = item / "uploads"
            if uploads_dir.exists():
                for file_path in uploads_dir.iterdir():
                    if file_path.is_file() and not file_path.name.startswith("."):
                        logger.info(f"Found file {file_path.name}")
                        # Check if already added
                        # We re-read registry to get latest state
                        current_app = application_service.get_application(app_id)
                        existing_docs = [d.filename for d in current_app.documents]
                        
                        if file_path.name in existing_docs:
                            logger.info("File already indexed.")
                            continue
                            
                        # Use add_document from service
                        with open(file_path, "rb") as f:
                            content = f.read()
                        
                        application_service.add_document(app_id, file_path.name, content)
                        logger.info(f"Added document {file_path.name}")

if __name__ == "__main__":
    import sys
    sys.path.append(os.getcwd()) # Ensure src is in path
    import datetime
    
    import_legacy_data()
