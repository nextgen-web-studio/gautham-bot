from aiogram import Router, F
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
