from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.bot.keyboards.admin import admin_settings_kb, admin_cancel_kb
from app.database.client import get_setting, set_setting

router = Router()

class AdminSettings(StatesGroup):
    waiting_for_affiliate = State()
    waiting_for_channel = State()

@router.callback_query(F.data == "admin_settings")
async def admin_settings_menu(callback: CallbackQuery, is_admin: bool, state: FSMContext):
    if not is_admin: return
    await state.clear()
    
    aff_link = get_setting("affiliate_link", "Not set")
    ch_link = get_setting("public_channel_link", "Not set")
    
    text = f"⚙️ SETTINGS\n\n🔗 Affiliate Link:\n{aff_link}\n\n📢 Public Channel:\n{ch_link}"
    await callback.message.edit_text(text, reply_markup=admin_settings_kb(), disable_web_page_preview=True)
    await callback.answer()

@router.callback_query(F.data == "admin_set_affiliate")
async def ask_affiliate(callback: CallbackQuery, is_admin: bool, state: FSMContext):
    if not is_admin: return
    await state.set_state(AdminSettings.waiting_for_affiliate)
    await callback.message.edit_text("🔗 Send me the new Affiliate Link (e.g. https://broker-qx.pro/?lid=...)", reply_markup=admin_cancel_kb())
    await callback.answer()

@router.message(AdminSettings.waiting_for_affiliate)
async def save_affiliate(message: Message, is_admin: bool, state: FSMContext):
    if not is_admin: return
    new_link = message.text.strip()
    set_setting("affiliate_link", new_link)
    await state.clear()
    await message.answer("✅ Affiliate link updated successfully!")
    
@router.callback_query(F.data == "admin_set_channel")
async def ask_channel(callback: CallbackQuery, is_admin: bool, state: FSMContext):
    if not is_admin: return
    await state.set_state(AdminSettings.waiting_for_channel)
    await callback.message.edit_text("📢 Send me the new Public Channel Link (e.g. https://t.me/...)", reply_markup=admin_cancel_kb())
    await callback.answer()

@router.message(AdminSettings.waiting_for_channel)
async def save_channel(message: Message, is_admin: bool, state: FSMContext):
    if not is_admin: return
    new_link = message.text.strip()
    set_setting("public_channel_link", new_link)
    await state.clear()
    await message.answer("✅ Public channel link updated successfully!")