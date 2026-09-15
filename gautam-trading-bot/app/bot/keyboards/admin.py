from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_dashboard_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📊 Dashboard", callback_data="admin_dashboard"), InlineKeyboardButton(text="👥 Users", callback_data="admin_users")],
        [InlineKeyboardButton(text="📸 Proof / Reviews", callback_data="admin_proof"), InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")],
        [InlineKeyboardButton(text="💬 Messages", callback_data="admin_messages"), InlineKeyboardButton(text="⚙️ Settings", callback_data="admin_settings")]
    ])

def back_to_admin_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_main"), InlineKeyboardButton(text="🏠 Main Menu", callback_data="admin_main")]
    ])from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def admin_settings_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="?? Edit Affiliate Link", callback_data="admin_set_affiliate")],
        [InlineKeyboardButton(text="?? Edit Channel Link", callback_data="admin_set_channel")],
        [InlineKeyboardButton(text="?? Back", callback_data="admin_main")]
    ])

def admin_cancel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="? Cancel", callback_data="admin_settings")]
    ])
