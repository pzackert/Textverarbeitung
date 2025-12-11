
import sys
import os

# Add project root to path
sys.path.append(os.getcwd())

try:
    from src.services.project_service import project_service
    print("Loading projects...")
    projects = project_service.list_projects()
    print(f"Loaded {len(projects)} projects.")
    
    for p in projects:
        print(f"Checking project {p.id} ({p.name})")
        
        # Simulate route logic
        doc_count = len(p.documents)
        print(f"  Docs: {doc_count}")
        
        updated = p.updated_at
        print(f"  Updated type: {type(updated)}")
        if updated:
             print(f"  Formatted: {updated.strftime('%d.%m.%Y')}")
             
except Exception as e:
    print(f"CRASHED: {e}")
    import traceback
    traceback.print_exc()
