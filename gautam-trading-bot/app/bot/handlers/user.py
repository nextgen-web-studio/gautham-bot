from aiogram import Router, F
from aiogram.filters import CommandStart
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
    
    welcome_msg = get_setting("welcome_message", "Welcome to Gautam Trading 👋").replace("\\n", "\n")
    await message.answer(welcome_msg)
    
    proofs = supabase.table("proof_content").select("*").eq("enabled", True).order("sort_order").execute().data
    for p in proofs:
        log_event(user.id, "PROOF_VIEW", {"proof_id": p["id"]})
        if p["content_type"] == "image":
            await message.answer_photo(p["file_id"], caption=p.get("caption", ""))
        elif p["content_type"] == "video":
            await message.answer_video(p["file_id"], caption=p.get("caption", ""))
        elif p["content_type"] == "text":
            await message.answer(p.get("caption", ""))
            
    public_channel = get_setting("public_channel_link", "https://t.me/yourpublicchannel")
    await message.answer("🚀 To get started, join our public channel and create your account.", reply_markup=create_account_kb(public_channel))

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
        
    log_event(message.from_user.id, "ID_VALID", {"input": user_id})
    log_event(message.from_user.id, "ID_SUBMITTED")
    supabase.table("users").update({"quotex_id": user_id, "quotex_id_submitted_at": "now()"}).eq("telegram_id", message.from_user.id).execute()
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