from aiogram import Router, F
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
    if not is_admin: return
    await callback.message.edit_text("🔐 GAUTAM TRADING ADMIN\n\nWelcome, Admin 👋", reply_markup=admin_dashboard_kb())
    await callback.answer()

@router.callback_query(F.data == "admin_dashboard")
async def admin_dashboard(callback: CallbackQuery, is_admin: bool):
    if not is_admin: return
    
    users_count = supabase.table("users").select("id", count="exact").execute().count or 0
    ids_count = supabase.table("users").select("id", count="exact").not_.is_("quotex_id", "null").execute().count or 0
    
    text = f"📊 GAUTAM TRADING DASHBOARD\n\n👥 Total Users: {users_count}\n🆔 IDs Submitted: {ids_count}"
    await callback.message.edit_text(text, reply_markup=back_to_admin_kb())
    await callback.answer()