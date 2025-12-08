from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from frontend.services.api_client import api_client
import markdown

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
            "health": health,
            "current_page": "chat"
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
        
        # Convert Markdown to HTML
        answer_html = markdown.markdown(
            response.get("answer", ""),
            extensions=['fenced_code', 'tables', 'nl2br']
        )
        
        return templates.TemplateResponse(
            request=request,
            name="partials/chat_message.html",
            context={
                "question": question,
                "answer": answer_html,
                "sources": response.get("sources", []),
                "citations": response.get("citations", [])
            }
        )
    except Exception as e:
        error_msg = str(e)
        if "Connection Error" in error_msg:
            error_msg = "LLM Service nicht erreichbar. Bitte stellen Sie sicher, dass Ollama läuft."
        elif "Timeout" in error_msg:
            error_msg = "Die Anfrage hat zu lange gedauert. Bitte versuchen Sie es mit einer kürzeren Frage erneut."
            
        return templates.TemplateResponse(
            request=request,
            name="partials/chat_error.html",
            context={"error_message": error_msg}
        )
