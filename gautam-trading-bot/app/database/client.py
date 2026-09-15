from supabase import create_client, Client
from app.config.settings import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)

def get_setting(key: str, default: str = "") -> str:
    res = supabase.table("bot_settings").select("value").eq("key", key).execute()
    if res.data:
        return res.data[0]["value"]
    return default

def set_setting(key: str, value: str):
    supabase.table("bot_settings").upsert({"key": key, "value": value}).execute()