import asyncio
import logging
from src.api.routers import settings
from src.services.knowledge_service import knowledge_service

# Configure logging
logging.basicConfig(level=logging.INFO)

async def test_delete():
    filename = "nospaces.txt"
    # Create dummy file to delete
    knowledge_service.save_file(filename, b"test content")
    print(f"File created: {filename}")
    
    print("Attempting to delete through API function...")
    try:
        await settings.delete_global_knowledge(filename)
        print("Delete Success!")
    except Exception as e:
        print(f"CAUGHT EXCEPTION: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_delete())
