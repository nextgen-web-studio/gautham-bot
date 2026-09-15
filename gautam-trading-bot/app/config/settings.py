from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_webhook_secret: str = "gautam123"
    supabase_url: str
    supabase_service_role_key: str
    backend_url: str = ""
    initial_admin_telegram_id: str = "5188160752"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()