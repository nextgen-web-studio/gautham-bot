import os

base_dir = r"C:\Users\shrid\.gemini\antigravity\scratch\nextgen-ai-bot"

files = {
    "requirements.txt": """aiogram>=3.4.1
fastapi>=0.110.0
uvicorn>=0.28.0
sqlalchemy>=2.0.29
asyncpg>=0.29.0
alembic>=1.13.1
pydantic>=2.6.4
pydantic-settings>=2.2.1
openai>=1.14.2
redis>=5.0.3
""",
    "Dockerfile": """FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
""",
    "docker-compose.yml": """version: '3.8'

services:
  bot:
    build: .
    env_file: .env
    ports:
      - "8000:8000"
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  db:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: nextgen
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5
""",
    ".env.example": """BOT_TOKEN=8537127845:AAEBm1Y1_KrGkkrUnd4MzUNhPzd07jZk11w
AI_API_KEY=your_openai_or_compatible_api_key
DATABASE_URL=postgresql+asyncpg://postgres:password@db:5432/nextgen
REDIS_URL=redis://redis:6379/0
WEBHOOK_URL=https://yourdomain.com/webhook
WEBHOOK_SECRET=your_secret_token
ADMIN_IDS=123456789,987654321
AI_BASE_URL=https://api.openai.com/v1
""",
    ".gitignore": """venv/
__pycache__/
*.pyc
.env
.idea/
.vscode/
""",
    "README.md": """# NextGen AI Assistant Bot

A production-ready Telegram AI assistant bot built with aiogram 3.x, FastAPI, and PostgreSQL.

## Features
- Ask AI questions
- Summarize text
- Rewrite text
- Correct grammar
- Generate content
- Translate text
- Change writing tone

## Installation
1. Clone the repository.
2. Copy `.env.example` to `.env` and fill in your variables.
3. Run `docker-compose up -d --build`.

## Deployment
Supports Webhook mode when `WEBHOOK_URL` is set, otherwise falls back to polling for local development.
""",
    "app/config.py": """from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

class Settings(BaseSettings):
    bot_token: str
    ai_api_key: str
    ai_base_url: str = "https://api.openai.com/v1"
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
""",
    "app/database/models.py": """from sqlalchemy import Column, Integer, String, DateTime, BigInteger, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, unique=True, index=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    last_active_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    request_count = Column(Integer, default=0)

class UsageLog(Base):
    __tablename__ = "usage_logs"

    id = Column(Integer, primary_key=True, index=True)
    telegram_user_id = Column(BigInteger, index=True)
    feature = Column(String)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
    input_tokens = Column(Integer, default=0)
    output_tokens = Column(Integer, default=0)
""",
    "app/database/database.py": """from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.database.models import Base

engine = create_async_engine(settings.database_url, echo=False)
async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with async_session() as session:
        yield session
""",
    "app/database/repositories.py": """from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update
from app.database.models import User, UsageLog
from datetime import datetime, timezone

async def get_or_create_user(session: AsyncSession, user_id: int, username: str, first_name: str) -> User:
    result = await session.execute(select(User).where(User.telegram_user_id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(telegram_user_id=user_id, username=username, first_name=first_name)
        session.add(user)
    else:
        user.username = username
        user.first_name = first_name
        user.last_active_at = datetime.now(timezone.utc)
    await session.commit()
    return user

async def increment_user_request(session: AsyncSession, user_id: int):
    stmt = update(User).where(User.telegram_user_id == user_id).values(
        request_count=User.request_count + 1,
        last_active_at=datetime.now(timezone.utc)
    )
    await session.execute(stmt)
    await session.commit()

async def log_usage(session: AsyncSession, user_id: int, feature: str, input_tokens: int = 0, output_tokens: int = 0):
    log = UsageLog(telegram_user_id=user_id, feature=feature, input_tokens=input_tokens, output_tokens=output_tokens)
    session.add(log)
    await session.commit()
""",
    "app/services/ai_service.py": """from openai import AsyncOpenAI
from app.config import settings

client = AsyncOpenAI(api_key=settings.ai_api_key, base_url=settings.ai_base_url)
# Default model, you can override depending on the provider
MODEL = "gpt-4o-mini" # Or compatible

async def _call_ai(system_prompt: str, user_prompt: str) -> str:
    try:
        response = await client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        import logging
        logging.error(f"AI API Error: {e}")
        return "⚠️ Something went wrong while processing your request. Please try again."

async def ask_ai(question: str) -> str:
    return await _call_ai("You are NextGen AI Assistant, a helpful, professional, and concise assistant.", question)

async def summarize_text(text: str) -> str:
    prompt = "Summarize the following text, providing the main point, important details, and key conclusions."
    return await _call_ai(prompt, text)

async def rewrite_text(text: str, style: str) -> str:
    prompt = f"Rewrite the following text in a {style} style while preserving its original meaning, names, numbers, and facts."
    return await _call_ai(prompt, text)

async def correct_grammar(text: str) -> str:
    prompt = "Correct grammar, spelling, punctuation, and clarity of the following text. Output ONLY the corrected text, followed by a brief '### Changes' section explaining major corrections."
    return await _call_ai(prompt, text)

async def generate_content(instructions: str) -> str:
    prompt = "You are a creative content generator. Generate useful content based on the following instructions."
    return await _call_ai(prompt, instructions)

async def translate_text(text: str, target_language: str) -> str:
    prompt = f"Translate the following text to {target_language}. Preserve the meaning and formatting of the original text."
    return await _call_ai(prompt, text)

async def change_tone(text: str, tone: str) -> str:
    prompt = f"Rewrite the following text using a {tone} tone."
    return await _call_ai(prompt, text)
""",
    "app/services/rate_limit.py": """# Simple in-memory rate limiting for V1
from cachetools import TTLCache
import time

# Allow 10 requests per minute per user
cache = TTLCache(maxsize=10000, ttl=60)

async def check_rate_limit(user_id: int) -> bool:
    current = cache.get(user_id, 0)
    if current >= 10:
        return False
    cache[user_id] = current + 1
    return True
""",
    "app/keyboards/main_menu.py": """from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_main_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💬 Ask AI", callback_data="feature_ask"), InlineKeyboardButton(text="📝 Rewrite", callback_data="feature_rewrite"), InlineKeyboardButton(text="📚 Summarize", callback_data="feature_summarize")],
        [InlineKeyboardButton(text="✍️ Generate", callback_data="feature_generate"), InlineKeyboardButton(text="✅ Grammar", callback_data="feature_grammar"), InlineKeyboardButton(text="🌍 Translate", callback_data="feature_translate")],
        [InlineKeyboardButton(text="🎨 Tone", callback_data="feature_tone"), InlineKeyboardButton(text="💡 More Tools", callback_data="feature_more")],
        [InlineKeyboardButton(text="❓ Help", callback_data="feature_help")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")]
    ])

def get_back_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")]
    ])

def get_rewrite_styles() -> InlineKeyboardMarkup:
    styles = ["Professional", "Simple", "Friendly", "Formal", "Shorter", "More Detailed"]
    keyboard = []
    for i in range(0, len(styles), 2):
        row = [InlineKeyboardButton(text=styles[i], callback_data=f"style_{styles[i]}")]
        if i+1 < len(styles):
            row.append(InlineKeyboardButton(text=styles[i+1], callback_data=f"style_{styles[i+1]}"))
        keyboard.append(row)
    keyboard.append([InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)
""",
    "app/handlers/start.py": """from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from app.keyboards.main_menu import get_main_menu
from app.database.database import async_session
from app.database.repositories import get_or_create_user

router = Router()

START_TEXT = '''<b>👋 Welcome to NextGen AI Assistant</b>

Your AI-powered text assistant on Telegram.

You can use me to:

💬 Ask questions
📝 Rewrite text
📚 Summarize content
✍️ Generate content
✅ Fix grammar
🌍 Translate text
🎨 Change writing tone
💡 Generate ideas

Choose an option below:'''

@router.message(Command("start"))
async def cmd_start(message: Message):
    async with async_session() as session:
        await get_or_create_user(session, message.from_user.id, message.from_user.username, message.from_user.first_name)
    await message.answer(START_TEXT, reply_markup=get_main_menu(), parse_mode="HTML")

@router.callback_query(F.data == "main_menu")
async def cq_main_menu(callback: CallbackQuery):
    await callback.message.edit_text(START_TEXT, reply_markup=get_main_menu(), parse_mode="HTML")
    await callback.answer()
""",
    "app/handlers/ask.py": """from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.keyboards.main_menu import get_back_menu
from app.services.ai_service import ask_ai
from app.services.rate_limit import check_rate_limit
from app.database.database import async_session
from app.database.repositories import increment_user_request, log_usage

router = Router()

class AskStates(StatesGroup):
    waiting_for_question = State()

@router.callback_query(F.data == "feature_ask")
async def ask_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(AskStates.waiting_for_question)
    await callback.message.edit_text("💬 What would you like to ask?", reply_markup=get_back_menu())
    await callback.answer()

@router.message(AskStates.waiting_for_question)
async def process_question(message: Message, state: FSMContext):
    if not await check_rate_limit(message.from_user.id):
        await message.answer("⏳ You've reached the current usage limit. Please try again later.")
        return
        
    await state.clear()
    wait_msg = await message.answer("🤔 Thinking...")
    
    response = await ask_ai(message.text)
    
    async with async_session() as session:
        await increment_user_request(session, message.from_user.id)
        await log_usage(session, message.from_user.id, "ask")
        
    await wait_msg.edit_text(response, reply_markup=get_back_menu())
""",
    "app/bot.py": """from aiogram import Bot, Dispatcher
from app.config import settings
from app.handlers import start, ask

bot = Bot(token=settings.bot_token)
dp = Dispatcher()

# Register handlers
dp.include_router(start.router)
dp.include_router(ask.router)
# Include other handlers as needed...

async def setup_bot():
    pass
""",
    "app/main.py": """import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram.types import Update
from app.config import settings
from app.bot import bot, dp, setup_bot
from app.database.database import init_db

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    await init_db()
    await setup_bot()
    
    if settings.webhook_url:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != settings.webhook_url:
            await bot.set_webhook(url=settings.webhook_url, secret_token=settings.webhook_secret)
        logging.info(f"Webhook set to {settings.webhook_url}")
    else:
        # For local testing via polling
        import asyncio
        asyncio.create_task(dp.start_polling(bot))
        logging.info("Started polling mode")
        
    yield
    
    if settings.webhook_url:
        await bot.delete_webhook()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook_handler(request: Request):
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if settings.webhook_secret and secret_token != settings.webhook_secret:
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
