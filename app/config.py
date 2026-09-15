from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    bot_token: str
    ai_api_key: str
    ai_base_url: str = "https://generativelanguage.googleapis.com/v1beta/openai/"
    database_url: str = "sqlite+aiosqlite:///./test.db" # Default fallback
    redis_url: str = ""
    webhook_url: str = ""
    webhook_secret: str = "secret"
    admin_ids: str = ""

    @property
    def admin_ids_list(self) -> List[int]:
        if not self.admin_ids:
            return []
        return [int(x.strip()) for x in self.admin_ids.split(",") if x.strip().isdigit()]

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
