from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from frontend.services.api_client import api_client
from src.services.chat_service import chat_service
from src.services.settings_service import settings_service
from src.core.models import ChatMessage
import markdown
from pathlib import Path

router = APIRouter(prefix="/chat", tags=["chat"])
# Fix template path
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(Path(__file__).parent.parent / "templates"))

@router.get("", response_class=HTMLResponse)
async def chat_page(request: Request):
    # Get system status for sidebar
    try:
        stats = await api_client.get_system_stats()
        health = await api_client.get_system_health()
    except Exception:
        stats = {}
        health = {"ollama_available": False, "chromadb_available": False}

    # Load Global Chat History
    chat_session = chat_service.get_chat_session(project_id=None)
    
    # Load Settings
    settings = settings_service.get_settings()

    return templates.TemplateResponse(
        request=request,
        name="chat.html",
        context={
            "stats": stats,
            "health": health,
            "current_page": "chat",
            "chat_history": chat_session.messages,
            "greeting_message": settings.greeting_message,
            "settings": settings,
            "model_name": "Qwen 2.5 (7B)" # Issue 8: Model Display
        }
    )

@router.post("/query", response_class=HTMLResponse)
async def chat_query(
    request: Request,
    question: str = Form(...)
):
    # 1. User Message
    user_msg = ChatMessage(role="user", content=question)
    chat_service.append_message(None, user_msg) # PID None = Global
    
    # Render user msg
    user_msg_html = templates.get_template("partials/chat_message.html").render(msg=user_msg)

    try:
        # Load Settings for System Prompt
        settings = settings_service.get_settings()
        
        # Call API
        response = await api_client.query_rag(
            question, 
            system_prompt=settings.system_prompt
        )
        
        # Convert Markdown to HTML
        answer_html = markdown.markdown(
            response.get("answer", ""),
            extensions=['fenced_code', 'tables', 'nl2br']
        )
        
        # 2. Assistant Message
        import random
        assistant_msg = ChatMessage(
            role="assistant", 
            content=answer_html,
            metadata={  # Mock Metadata (Issue 7)
                "tokens_per_sec": round(random.uniform(22.0, 28.0), 2),
                "total_tokens": len(answer_html.split()) * 2,
                "time_to_first_token": f"{round(random.uniform(0.3, 0.9), 2)}s",
                "stop_reason": "stop"
            }
        )
        chat_service.append_message(None, assistant_msg)

        assistant_msg_html = templates.get_template("partials/chat_message.html").render(msg=assistant_msg)
        
        return HTMLResponse(content=user_msg_html + assistant_msg_html)

    except Exception as e:
        error_msg = str(e)
        if "Connection Error" in error_msg:
            error_msg = "LLM Service nicht erreichbar. Bitte stellen Sie sicher, dass Ollama läuft."
        elif "Timeout" in error_msg:
            error_msg = "Die Anfrage hat zu lange gedauert. Bitte versuchen Sie es mit einer kürzeren Frage erneut."
            
        # Error handling - maybe render a specific error message type or just standard assistant error?
        # For consistency, we might want to log the error to chat too? 
        # For now, stick to original error partial if possible, or just plain text.
        return templates.TemplateResponse(
            request=request,
            name="partials/chat_error.html",
            context={"error_message": error_msg}
        )
