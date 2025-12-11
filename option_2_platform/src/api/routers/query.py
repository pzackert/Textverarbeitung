import time
import logging
from fastapi import APIRouter, Depends, HTTPException, status
from src.api.schemas import QueryRequest, QueryResponse, SourceInfo, Citation
from src.api.dependencies import get_llm_chain
from src.rag.llm_chain import LLMChain

router = APIRouter(prefix="/query", tags=["query"])
logger = logging.getLogger(__name__)

@router.post("", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    llm_chain: LLMChain = Depends(get_llm_chain)
):
    """
    Execute a RAG query.
    """
    if not request.question.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Question cannot be empty"
        )
        
    logger.info(f"Query received: {request.question[:50]}...")
    start_time = time.time()
    
    try:
        # Execute query
        result = llm_chain.query(
            question=request.question,
            template_type=request.template_type,
            top_k=request.top_k,
            system_prompt=request.system_prompt
        )
        
        # Parse result
        # Assuming result structure from LLMChain.query
        # It returns Dict[str, Any] with keys like 'answer', 'sources', 'metadata'
        
        answer = result.get("answer", "")
        sources_data = result.get("sources", [])
        metadata = result.get("metadata", {})
        
        # Map sources to SourceInfo
        sources = []
        for s in sources_data:
            sources.append(SourceInfo(
                source_file=s.get("source", "unknown"),
                page_number=s.get("page"),
                chunk_id=s.get("chunk_id", 0),
                score=s.get("score")
            ))
            
        # Create citations (simplified mapping for now)
        citations = []
        for i, s in enumerate(sources):
            citations.append(Citation(
                citation_number=i+1,
                source=s
            ))
            
        total_time = (time.time() - start_time) * 1000
        metadata["total_time_ms"] = total_time
        
        logger.info(f"Response generated: {len(answer)} chars")
        
        return QueryResponse(
            answer=answer,
            sources=sources,
            citations=citations,
            metadata=metadata
        )
        
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
