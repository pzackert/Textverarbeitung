import os
import shutil
import logging
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from src.api.schemas import IngestResponse
from src.api.dependencies import get_ingestion_pipeline
from src.rag.ingestion import IngestionPipeline

router = APIRouter(prefix="/ingest", tags=["ingest"])
logger = logging.getLogger(__name__)

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".xlsx"}
UPLOAD_DIR = "data/input"

@router.post("/upload", response_model=IngestResponse)
async def upload_document(
    file: UploadFile = File(...),
    pipeline: IngestionPipeline = Depends(get_ingestion_pipeline)
):
    """
    Upload and ingest a document.
    """
    filename = file.filename
    logger.info(f"File uploaded: {filename}")
    
    # Validate extension
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file extension: {ext}. Allowed: {ALLOWED_EXTENSIONS}"
        )
        
    # Ensure upload directory exists
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(UPLOAD_DIR, filename)
    
    try:
        # Save file
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        logger.info(f"Processing started: {filename}")
        
        # Run ingestion
        # Note: In a real app, this should be a background task
        chunks = pipeline.ingest_file(file_path)
        
        logger.info(f"Processing complete: {len(chunks)} chunks")
        
        return IngestResponse(
            success=True,
            file_path=file_path,
            chunks_count=len(chunks),
            message="Document processed successfully"
        )
        
    except Exception as e:
        logger.error(f"Processing failed: {e}")
        # Clean up if needed, but keeping the file might be useful for debugging
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
