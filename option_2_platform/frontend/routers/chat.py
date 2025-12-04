from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from frontend.services.api_client import api_client

router = APIRouter(prefix="/chat", tags=["chat"])
templates = Jinja2Templates(directory="frontend/templates")

@router.get("", response_class=HTMLResponse)
async def chat_page(request: Request):
    # Get system status for sidebar
    try:
        stats = await api_client.get_system_stats()
        health = await api_client.get_system_health()
    except Exception:
        stats = {}
        health = {"ollama_available": False, "chromadb_available": False}

    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "stats": stats,
            "health": health
        }
    )

@router.post("/query", response_class=HTMLResponse)
async def chat_query(
    request: Request,
    question: str = Form(...)
):
    try:
        # Call API
        response = await api_client.query_rag(question)
        
        return templates.TemplateResponse(
            request=request,
            name="partials/chat_message.html",
            context={
                "question": question,
                "answer": response.get("answer"),
                "sources": response.get("sources", []),
                "citations": response.get("citations", [])
            }
        )
    except Exception as e:
        return HTMLResponse(f"""
            <div class="p-4 mb-4 text-sm text-red-800 rounded-lg bg-red-50" role="alert">
                <span class="font-medium">Error:</span> {str(e)}
            </div>
        """)
