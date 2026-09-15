from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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