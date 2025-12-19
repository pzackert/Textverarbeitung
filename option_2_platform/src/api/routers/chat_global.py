import logging
import uuid
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/chat/global", tags=["chat_global"])
logger = logging.getLogger(__name__)

# --- Schemas ---
class GlobalChatMessage(BaseModel):
    role: str # "user" or "assistant"
    content: str
    timestamp: str

class ChatSession(BaseModel):
    chat_id: str
    title: str
    updated_at: str
    messages: List[GlobalChatMessage] = []

class SendMessageRequest(BaseModel):
    message: str
    include_rag: bool = False
    use_base_documents: bool = True

class SendMessageResponse(BaseModel):
    response: str
    timestamp: str

# --- In-Memory Store (for now, file based later) ---
# Note: In real app, persist this to disk/db
global_chat_store: List[ChatSession] = []

@router.get("/list", response_model=List[dict])
async def list_chats():
    # Return summaries
    return [
        {
            "chat_id": c.chat_id,
            "title": c.title,
            "last_message": c.messages[-1].content[:50] + "..." if c.messages else "New Chat",
            "updated_at": c.updated_at
        }
        for c in sorted(global_chat_store, key=lambda x: x.updated_at, reverse=True)
    ]

@router.post("/create", response_model=ChatSession)
async def create_chat():
    new_chat = ChatSession(
        chat_id=str(uuid.uuid4()),
        title="New Chat",
        updated_at=datetime.utcnow().isoformat()
    )
    global_chat_store.append(new_chat)
    return new_chat

@router.get("/{chat_id}/history", response_model=dict)
async def get_history(chat_id: str):
    chat = next((c for c in global_chat_store if c.chat_id == chat_id), None)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"messages": chat.messages}

@router.post("/{chat_id}/message", response_model=SendMessageResponse)
async def send_message(chat_id: str, request: SendMessageRequest):
    chat = next((c for c in global_chat_store if c.chat_id == chat_id), None)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    # 1. Add User Message
    timestamp = datetime.utcnow().isoformat()
    chat.messages.append(GlobalChatMessage(role="user", content=request.message, timestamp=timestamp))
    
    # Update title if first message
    if len(chat.messages) == 1:
        chat.title = request.message[:30] + "..."

    # 2. Generate Logic (Mock for Phase 1)
    # TODO: Connect to LLM Service / Base Documents
    response_text = f"Simulated response to: {request.message}\n(Base Docs: {request.use_base_documents})"
    
    # 3. Add Assistant Message
    chat.messages.append(GlobalChatMessage(role="assistant", content=response_text, timestamp=timestamp))
    chat.updated_at = timestamp

    return SendMessageResponse(response=response_text, timestamp=timestamp)

@router.delete("/{chat_id}")
async def delete_chat(chat_id: str):
    global global_chat_store
    global_chat_store = [c for c in global_chat_store if c.chat_id != chat_id]
    return {"status": "deleted"}
