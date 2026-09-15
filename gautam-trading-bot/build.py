import os

base_dir = r"C:\Users\Shridharsan\.gemini\antigravity\scratch\gautham-bot\gautham-bot-main\gautam-trading-bot"

files = {
    "requirements.txt": """aiogram>=3.4.1
fastapi>=0.110.0
uvicorn>=0.28.0
pydantic>=2.6.4
pydantic-settings>=2.2.1
supabase>=2.3.4
apscheduler>=3.10.4
python-dotenv>=1.0.1""",
    
    "Dockerfile": """FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]""",

    "render.yaml": """services:
  - type: web
    name: gautam-trading-bot
    env: docker
    plan: free""",

    "schema.sql": """-- Run this in Supabase SQL Editor
CREATE TABLE IF NOT EXISTS bot_settings (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS admins (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    name TEXT,
    role TEXT DEFAULT 'admin',
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    telegram_id BIGINT UNIQUE NOT NULL,
    username TEXT,
    first_name TEXT,
    last_name TEXT,
    language_code TEXT,
    source TEXT,
    started_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_active_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    affiliate_clicked BOOLEAN DEFAULT FALSE,
    account_button_clicked BOOLEAN DEFAULT FALSE,
    quotex_id TEXT,
    quotex_id_submitted_at TIMESTAMP WITH TIME ZONE,
    status TEXT DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS proof_content (
    id SERIAL PRIMARY KEY,
    content_type TEXT NOT NULL, -- image, video, text
    file_id TEXT,
    storage_url TEXT,
    caption TEXT,
    sort_order INTEGER DEFAULT 0,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_events (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id),
    event_type TEXT NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS user_reminders (
    id SERIAL PRIMARY KEY,
    user_id BIGINT REFERENCES users(telegram_id),
    reminder_type TEXT,
    last_sent_at TIMESTAMP WITH TIME ZONE,
    reminder_count INTEGER DEFAULT 0,
    enabled BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Insert defaults
INSERT INTO bot_settings (key, value) VALUES 
('affiliate_link', 'https://broker-qx.pro/?lid=2092326'),
('welcome_message', 'Welcome to Gautam Trading 👋\n\nGet access to our trading resources and updates.\n\nBefore continuing, take a look at the information and reviews below.'),
('quotex_id_exact_digits', '7'),
('reminders_enabled', 'true'),
('reminder_interval_minutes', '60'),
('maximum_reminders', '3')
ON CONFLICT (key) DO NOTHING;

-- Insert initial admin
INSERT INTO admins (telegram_id, name, enabled) VALUES (5188160752, 'Shri Dharsan', true) ON CONFLICT (telegram_id) DO NOTHING;
""",

    "app/config/settings.py": """from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    telegram_bot_token: str
    telegram_webhook_secret: str = "secret"
    supabase_url: str
    supabase_service_role_key: str
    backend_url: str = ""
    initial_admin_telegram_id: str = "5188160752"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

settings = Settings()
""",
    
    "app/database/client.py": """from supabase import create_client, Client
from app.config.settings import settings

supabase: Client = create_client(settings.supabase_url, settings.supabase_service_role_key)

def get_setting(key: str, default: str = "") -> str:
    res = supabase.table("bot_settings").select("value").eq("key", key).execute()
    if res.data:
        return res.data[0]["value"]
    return default

def set_setting(key: str, value: str):
    supabase.table("bot_settings").upsert({"key": key, "value": value}).execute()
""",

    "app/bot/middlewares/admin.py": """from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Callable, Dict, Any, Awaitable
from app.database.client import supabase

class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message, data: Dict[str, Any]) -> Any:
        res = supabase.table("admins").select("enabled").eq("telegram_id", event.from_user.id).execute()
        is_admin = False
        if res.data and res.data[0].get("enabled") == True:
            is_admin = True
        
        data['is_admin'] = is_admin
        return await handler(event, data)
""",

    "app/bot/keyboards/user.py": """from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_account_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚀 Create Account", callback_data="action_create_account")],
        [InlineKeyboardButton(text="✅ I've Created My Account", callback_data="action_account_created")]
    ])

def stop_reminders_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Submit ID", callback_data="action_account_created")],
        [InlineKeyboardButton(text="❌ Stop Reminders", callback_data="action_stop_reminders")]
    ])
""",
    
    "app/bot/keyboards/admin.py": """from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_dashboard_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Dashboard", callback_data="admin_dashboard"), InlineKeyboardButton(text="👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton(text="📸 Proof / Reviews", callback_data="admin_proof"), InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="💬 Messages", callback_data="admin_messages"), InlineKeyboardButton(text="⏰ Reminders", callback_data="admin_reminders")],
        [InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_settings"), InlineKeyboardButton(text="📈 Analytics", callback_data="admin_analytics")],
        [InlineKeyboardButton(text="🛡️ Admins", callback_data="admin_admins"), InlineKeyboardButton(text="📋 Activity Logs", callback_data="admin_logs")]
    ])

def back_to_admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_main"), InlineKeyboardButton(text="🏠 Main Menu", callback_data="admin_main")]
    ])
""",

    "app/bot/handlers/user.py": """from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.database.client import supabase, get_setting
from app.bot.keyboards.user import create_account_kb, stop_reminders_kb
import re

router = Router()

class UserStates(StatesGroup):
    waiting_for_id = State()

def log_event(user_id: int, event_type: str, metadata: dict = None):
    supabase.table("user_events").insert({"user_id": user_id, "event_type": event_type, "metadata": metadata or {}}).execute()

@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    source = message.text.replace("/start", "").strip()
    
    # Upsert user
    user_data = {
        "telegram_id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "language_code": user.language_code,
        "last_active_at": "now()"
    }
    if source:
        user_data["source"] = source
        
    res = supabase.table("users").select("id").eq("telegram_id", user.id).execute()
    if not res.data:
        supabase.table("users").insert(user_data).execute()
    else:
        supabase.table("users").update({"last_active_at": "now()"}).eq("telegram_id", user.id).execute()

    log_event(user.id, "START", {"source": source})
    
    # Send welcome
    welcome_msg = get_setting("welcome_message", "Welcome to Gautam Trading 👋")
    await message.answer(welcome_msg)
    
    # Send proofs
    proofs = supabase.table("proof_content").select("*").eq("enabled", True).order("sort_order").execute().data
    for p in proofs:
        log_event(user.id, "PROOF_VIEW", {"proof_id": p["id"]})
        if p["content_type"] == "image":
            await message.answer_photo(p["file_id"], caption=p.get("caption", ""))
        elif p["content_type"] == "video":
            await message.answer_video(p["file_id"], caption=p.get("caption", ""))
        elif p["content_type"] == "text":
            await message.answer(p.get("caption", ""))
            
    await message.answer("🚀 To get started, create your account and verify it.", reply_markup=create_account_kb())

@router.callback_query(F.data == "action_create_account")
async def create_account(callback: CallbackQuery):
    log_event(callback.from_user.id, "CREATE_ACCOUNT_CLICK")
    supabase.table("users").update({"account_button_clicked": True}).eq("telegram_id", callback.from_user.id).execute()
    affiliate_link = get_setting("affiliate_link", "https://broker-qx.pro/?lid=2092326")
    await callback.message.answer(f"Please sign up using this link:\n{affiliate_link}\n\nWhen you're ready, click 'I've Created My Account' on the previous menu.")
    await callback.answer()

@router.callback_query(F.data == "action_account_created")
async def account_created(callback: CallbackQuery, state: FSMContext):
    log_event(callback.from_user.id, "ID_REQUESTED")
    # Init reminder
    supabase.table("user_reminders").upsert({"user_id": callback.from_user.id, "reminder_type": "id_submit", "enabled": True}).execute()
    
    await state.set_state(UserStates.waiting_for_id)
    await callback.message.answer("🆔 Please enter your Quotex ID.\n\nEnter the ID exactly as shown in your account.")
    await callback.answer()

@router.message(UserStates.waiting_for_id)
async def process_id(message: Message, state: FSMContext):
    user_id = message.text.strip()
    required_digits = get_setting("quotex_id_exact_digits", "7")
    
    if not re.match(f"^[0-9]{{{required_digits}}}$", user_id):
        log_event(message.from_user.id, "ID_INVALID", {"input": user_id})
        await message.answer(f"❌ Invalid Quotex ID\n\nPlease enter your ID using exactly {required_digits} digits.\nExample:\n{'1' * int(required_digits)}")
        return
        
    # Valid ID
    log_event(message.from_user.id, "ID_VALID", {"input": user_id})
    log_event(message.from_user.id, "ID_SUBMITTED")
    supabase.table("users").update({"quotex_id": user_id, "quotex_id_submitted_at": "now()"}).eq("telegram_id", message.from_user.id).execute()
    # Disable reminders
    supabase.table("user_reminders").update({"enabled": False}).eq("user_id", message.from_user.id).execute()
    
    await state.clear()
    valid_msg = get_setting("valid_id_message", "✅ Quotex ID received successfully.\n\nYour ID has been saved.\nYou can now continue using Gautam Trading.")
    await message.answer(valid_msg)

@router.callback_query(F.data == "action_stop_reminders")
async def stop_reminders(callback: CallbackQuery):
    log_event(callback.from_user.id, "REMINDER_DISABLED")
    supabase.table("user_reminders").update({"enabled": False}).eq("user_id", callback.from_user.id).execute()
    await callback.message.edit_text("Reminders stopped.\n\nYou can continue whenever you're ready.")
    await callback.answer()
""",
    
    "app/bot/handlers/admin.py": """from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from app.bot.keyboards.admin import admin_dashboard_kb, back_to_admin_kb
from app.database.client import supabase, get_setting, set_setting

router = Router()

@router.message(Command("admin"))
async def cmd_admin(message: Message, is_admin: bool):
    if not is_admin:
        await message.answer("❌ You are not authorized to access this section.")
        return
    await message.answer("🔐 GAUTAM TRADING ADMIN\n\nWelcome, Admin 👋", reply_markup=admin_dashboard_kb())

@router.callback_query(F.data == "admin_main")
async def admin_main(callback: CallbackQuery, is_admin: bool):
    if not is_admin:
        return
    await callback.message.edit_text("🔐 GAUTAM TRADING ADMIN\n\nWelcome, Admin 👋", reply_markup=admin_dashboard_kb())
    await callback.answer()

@router.callback_query(F.data == "admin_dashboard")
async def admin_dashboard(callback: CallbackQuery, is_admin: bool):
    if not is_admin: return
    
    users_count = supabase.table("users").select("id", count="exact").execute().count
    ids_count = supabase.table("users").select("id", count="exact").not_.is_("quotex_id", "null").execute().count
    
    text = f"📊 GAUTAM TRADING\n\n👥 Total Users: {users_count}\n🆔 IDs Submitted: {ids_count}"
    await callback.message.edit_text(text, reply_markup=back_to_admin_kb())
    await callback.answer()

# Further admin routes for Proofs, Settings, Broadcasts can be built out here following the same pattern
""",
    
    "app/main.py": """import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from app.config.settings import settings
from app.bot.handlers import user, admin
from app.bot.middlewares.admin import AdminMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database.client import supabase, get_setting
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()

# Middlewares
dp.message.middleware(AdminMiddleware())
dp.callback_query.middleware(AdminMiddleware())

# Routers
dp.include_router(admin.router)
dp.include_router(user.router)

scheduler = AsyncIOScheduler()

async def reminder_job():
    reminders_enabled = get_setting("reminders_enabled", "true").lower() == "true"
    if not reminders_enabled: return
    
    interval = int(get_setting("reminder_interval_minutes", "60"))
    max_reminders = int(get_setting("maximum_reminders", "3"))
    
    # Very basic reminder check (in production use proper DB time functions)
    res = supabase.table("user_reminders").select("*").eq("enabled", True).execute()
    for rem in res.data:
        if rem["reminder_count"] >= max_reminders:
            supabase.table("user_reminders").update({"enabled": False}).eq("id", rem["id"]).execute()
            continue
            
        last_sent = rem["last_sent_at"] or rem["created_at"]
        # If enough time has passed, send reminder
        # Note: robust implementation requires timezone-aware datetime parsing
        
        # await bot.send_message(rem["user_id"], "You haven't completed the Quotex ID submission yet.", reply_markup=stop_reminders_kb())
        # supabase.table("user_reminders").update({"reminder_count": rem["reminder_count"] + 1, "last_sent_at": "now()"}).eq("id", rem["id"]).execute()
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup scheduler
    scheduler.add_job(reminder_job, 'interval', minutes=10)
    scheduler.start()
    
    if settings.backend_url:
        webhook_url = f"{settings.backend_url}/webhook"
        await bot.set_webhook(url=webhook_url, secret_token=settings.telegram_webhook_secret)
        logging.info(f"Webhook set to {webhook_url}")
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        asyncio.create_task(dp.start_polling(bot))
        logging.info("Started polling mode")
        
    yield
    
    scheduler.shutdown()
    if settings.backend_url:
        await bot.delete_webhook()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook_handler(request: Request):
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if settings.telegram_webhook_secret and secret_token != settings.telegram_webhook_secret:
        return {"status": "unauthorized"}
        
    update_data = await request.json()
    update = Update(**update_data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
"""
}

for filepath, content in files.items():
    full_path = os.path.join(base_dir, filepath)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Files generated successfully.")