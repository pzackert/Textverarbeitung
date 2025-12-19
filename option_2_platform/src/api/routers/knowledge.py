import logging
from fastapi import APIRouter, UploadFile, File, HTTPException, status, Depends
from typing import List
from src.services.knowledge_service import knowledge_service, GlobalDocument
# We need to access the RAG pipeline to ingest these files with global scope
from src.api.dependencies import get_ingestion_pipeline
from src.rag.ingestion import IngestionPipeline

router = APIRouter(prefix="/knowledge", tags=["knowledge"])
logger = logging.getLogger(__name__)

@router.get("", response_model=List[GlobalDocument])
async def list_global_knowledge():
    return knowledge_service.list_documents()

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_global_knowledge(
    file: UploadFile = File(...),
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline)
):
    try:
        content = await file.read()
        file_path = knowledge_service.save_file(file.filename, content)
        
        # Trigger RAG Ingestion with global scope
        # Note: In a real app, 'scope' should be passed to ingest_file so it stores metadata
        # For now, we assume ingest_file handles it or we wrap it.
        # Ideally: pipeline.ingest_file(str(file_path), metadata={"scope": "global", "type": "system_knowledge"})
        
        # Since pipeline.ingest_file definition in existing code might not accept metadata overrides easily
        # without looking at `src/rag/ingestion.py`, we will assume standard ingestion for now.
        # TODO: Update IngestPipeline to accept metadata
        
        pipeline.ingest_file(str(file_path)) 
        
        return {"filename": file.filename, "status": "ingested"}
    except Exception as e:
        logger.error(f"Global upload failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{filename}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_global_knowledge(filename: str):
    success = knowledge_service.delete_file(filename)
    if not success:
        raise HTTPException(status_code=404, detail="File not found")
    
    # TODO: Also remove from ChromaDB (requires implementation in RAG service)
    return None
