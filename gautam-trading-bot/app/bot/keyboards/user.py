from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def create_account_kb(public_channel_url: str) -> InlineKeyboardMarkup:
    buttons = []
    if public_channel_url:
        buttons.append([InlineKeyboardButton(text="📢 Join Public Channel", url=public_channel_url)])
    
    buttons.append([InlineKeyboardButton(text="🚀 Create Account", callback_data="action_create_account")])
    buttons.append([InlineKeyboardButton(text="✅ I've Created My Account", callback_data="action_account_created")])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

def stop_reminders_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Submit ID", callback_data="action_account_created")],
        [InlineKeyboardButton(text="❌ Stop Reminders", callback_data="action_stop_reminders")]
    ])