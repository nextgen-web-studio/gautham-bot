from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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

def get_more_tools_menu() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📧 Email Writer", callback_data="feature_generate_email"), InlineKeyboardButton(text="📱 Social Post", callback_data="feature_generate_social")],
        [InlineKeyboardButton(text="🔤 Make Shorter", callback_data="feature_rewrite_shorter"), InlineKeyboardButton(text="📖 Make Longer", callback_data="feature_rewrite_longer")],
        [InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")]
    ])
