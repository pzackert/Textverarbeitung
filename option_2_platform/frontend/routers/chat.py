from fastapi import APIRouter, Request, HTTPException, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path
from frontend.services.api_client import api_client

router = APIRouter(prefix="/chat", tags=["frontend_chat"])

BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

@router.get("", response_class=HTMLResponse)
async def chat_page(request: Request):
    """
    Renders the Global Chat interface.
    """
    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={} 
    )


@router.post("/query", response_class=HTMLResponse)
async def chat_query(request: Request, question: str = Form(...)):
    """Proxy chat queries to the backend RAG API (mocked in tests)."""
    result = {}
    try:
        res = api_client.query_rag(question)
        result = await res if hasattr(res, "__await__") else res
    except Exception:
        result = {}

    answer = result.get("answer", "") if isinstance(result, dict) else ""
    sources = result.get("sources", []) if isinstance(result, dict) else []

    body = f"<div><p>{answer}</p>" + "".join(
        f"<span>{s.get('source') or s.get('source_file') or ''}</span>" for s in sources
    ) + "</div>"
    return HTMLResponse(content=body)
