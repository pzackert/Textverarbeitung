import json
from pathlib import Path
from src.core.models import Settings

class SettingsService:
    def __init__(self):
        self.storage_path = Path("data/config/settings.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
    def get_settings(self) -> Settings:
        if not self.storage_path.exists():
            return Settings()
        
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                return Settings(**data)
        except Exception:
            return Settings()
            
    def save_settings(self, settings: Settings) -> Settings:
        with open(self.storage_path, 'w') as f:
            f.write(settings.model_dump_json(indent=2))
        return settings

    def update_settings(self, greeting_message: str, system_prompt: str) -> Settings:
        settings = Settings(
            greeting_message=greeting_message,
            system_prompt=system_prompt
        )
        return self.save_settings(settings)

settings_service = SettingsService()
