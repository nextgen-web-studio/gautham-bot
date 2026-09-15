from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.database.client import supabase
from app.bot.keyboards.admin import back_to_admin_kb
import asyncio

router = Router()

class BroadcastStates(StatesGroup):
    waiting_for_message = State()

@router.callback_query(F.data == "admin_users")
async def view_users(callback: CallbackQuery, is_admin: bool):
    if not is_admin: return
    
    recent_users = supabase.table("users").select("telegram_id, username, quotex_id").order("created_at", desc=True).limit(5).execute()
    
    text = "👥 RECENT USERS\n\n"
    if recent_users.data:
        for u in recent_users.data:
            q_id = u.get('quotex_id') or "Not submitted"
            username = f"@{u.get('username')}" if u.get('username') else str(u.get('telegram_id'))
            text += f"👤 {username} | ID: {q_id}\n"
    else:
        text += "No users found."
        
    await callback.message.edit_text(text, reply_markup=back_to_admin_kb())
    await callback.answer()

@router.callback_query(F.data == "admin_broadcast")
async def start_broadcast(callback: CallbackQuery, is_admin: bool, state: FSMContext):
    if not is_admin: return
    await state.set_state(BroadcastStates.waiting_for_message)
    await callback.message.edit_text("📢 Send me the message you want to broadcast to ALL users (or send /cancel):")
    await callback.answer()

@router.message(BroadcastStates.waiting_for_message)
async def process_broadcast(message: Message, is_admin: bool, state: FSMContext):
    if not is_admin: return
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Broadcast cancelled.")
        return
        
    await state.clear()
    await message.answer("📢 Starting broadcast... this may take a while depending on user count.")
    
    users = supabase.table("users").select("telegram_id").execute()
    success = 0
    failed = 0
    
    for u in users.data:
        try:
            await message.bot.copy_message(chat_id=u["telegram_id"], from_chat_id=message.chat.id, message_id=message.message_id)
            success += 1
            await asyncio.sleep(0.05) # Prevent rate limits
        except Exception:
            failed += 1
            
    await message.answer(f"✅ Broadcast Complete!\n\nDelivered: {success}\nFailed: {failed}")