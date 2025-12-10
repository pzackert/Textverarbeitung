import json
from pathlib import Path
from typing import Optional
from datetime import datetime
from src.core.models import ChatSession, ChatMessage

class ChatService:
    def __init__(self):
        self.storage_dir = Path("data/chats")
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def _get_file_path(self, project_id: Optional[str] = None) -> Path:
        filename = f"{project_id}.json" if project_id else "global.json"
        return self.storage_dir / filename

    def get_chat_session(self, project_id: Optional[str] = None) -> ChatSession:
        """Load chat session or create new one if not exists."""
        file_path = self._get_file_path(project_id)
        
        if not file_path.exists():
            return ChatSession(project_id=project_id)

        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                return ChatSession(**data)
        except (json.JSONDecodeError, Exception) as e:
            print(f"Error loading chat session {file_path}: {e}")
            return ChatSession(project_id=project_id)

    def save_chat_session(self, session: ChatSession):
        """Save chat session to file."""
        file_path = self._get_file_path(session.project_id)
        session.updated_at = datetime.now()
        
        with open(file_path, 'w') as f:
            f.write(session.model_dump_json(indent=2))

    def append_message(self, project_id: Optional[str], message: ChatMessage) -> ChatSession:
        """Append a message to the session and save."""
        session = self.get_chat_session(project_id)
        session.messages.append(message)
        self.save_chat_session(session)
        return session

    def clear_history(self, project_id: Optional[str] = None):
        """Clear chat history (mostly for testing)."""
        file_path = self._get_file_path(project_id)
        if file_path.exists():
            file_path.unlink()

# Singleton
chat_service = ChatService()
