import asyncio
import os
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from supabase import create_client, Client

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)

def get_main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Reviews", callback_data="menu_reviews")],
        [InlineKeyboardButton(text="📊 About Us", callback_data="menu_about")],
        [InlineKeyboardButton(text="🔗 Get Started", callback_data="menu_affiliate")],
        [InlineKeyboardButton(text="💬 Support", callback_data="menu_support")]
    ])

@dp.message(CommandStart())
async def cmd_start(message: types.Message):
    telegram_id = str(message.from_user.id)
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Check if user exists
    user_res = supabase.table("users").select("*").eq("telegram_id", telegram_id).execute()
    
    if not user_res.data:
        # Extract source if passed e.g. /start ad_campaign_123
        source = None
        parts = message.text.split(" ")
        if len(parts) > 1:
            source = parts[1]
            
        supabase.table("users").insert({
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
            "last_name": last_name,
            "source": source,
            "status": "active"
        }).execute()
    else:
        # Update active time
        supabase.table("users").update({"status": "active"}).eq("telegram_id", telegram_id).execute()

    welcome_msg = (
        "👋 Welcome to Gautam Trading!\n\n"
        "Thanks for joining us. 😊\n\n"
        "Here you can:\n"
        "📊 Learn more about our trading community\n"
        "⭐ Check user reviews\n"
        "🔗 Access our recommended platform\n"
        "📢 Receive important updates\n\n"
        "Choose an option below 👇"
    )
    await message.answer(welcome_msg, reply_markup=get_main_menu())

@dp.callback_query(F.data == "menu_about")
async def show_about(callback: types.CallbackQuery):
    about_text = (
        "📊 About Gautam Trading\n\n"
        "Gautam Trading provides trading-related information, educational content, "
        "community updates and access to a recommended trading platform.\n\n"
        "Trading involves financial risk. Please understand the risks and terms "
        "of any platform before using it."
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⭐ Reviews", callback_data="menu_reviews")],
        [InlineKeyboardButton(text="🔗 Get Started", callback_data="menu_affiliate")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="menu_back")]
    ])
    await callback.message.edit_text(about_text, reply_markup=markup)
    await callback.answer()

@dp.callback_query(F.data == "menu_back")
async def go_back(callback: types.CallbackQuery):
    welcome_msg = (
        "👋 Welcome to Gautam Trading!\n\n"
        "Thanks for joining us. 😊\n\n"
        "Choose an option below 👇"
    )
    await callback.message.edit_text(welcome_msg, reply_markup=get_main_menu())
    await callback.answer()

@dp.callback_query(F.data == "menu_affiliate")
async def show_affiliate(callback: types.CallbackQuery):
    telegram_id = str(callback.from_user.id)
    
    # Track the click
    supabase.table("affiliate_clicks").insert({
        "telegram_id": telegram_id
    }).execute()
    
    # Fetch affiliate URL from settings, or fallback to env
    settings_res = supabase.table("bot_settings").select("setting_value").eq("setting_key", "affiliate_url").execute()
    affiliate_url = os.getenv("AFFILIATE_URL", "https://example.com/trading")
    if settings_res.data:
        affiliate_url = settings_res.data[0].get("setting_value", affiliate_url)
    
    disclosure_msg = (
        "🔗 Get Started\n\n"
        "You can access the recommended platform using the link below.\n\n"
        "ℹ️ This is an affiliate link. Gautam Trading may receive a commission if you register through this link.\n\n"
        "Trading involves risk. Please understand the platform and associated risks before depositing or trading.\n\n"
        "👇 Continue:"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Open Platform", url=affiliate_url)],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="menu_back")]
    ])
    await callback.message.edit_text(disclosure_msg, reply_markup=markup)
    await callback.answer()

@dp.callback_query(F.data == "menu_support")
async def show_support(callback: types.CallbackQuery, state: FSMContext = None):
    # For a real implementation, we would use FSM to catch the next message
    # For now, we will just prompt the user
    support_msg = (
        "💬 Support\n\n"
        "Send your question below and our support team will review it.\n\n"
        "Please type your message (start with /ask followed by your question):"
    )
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="menu_back")]
    ])
    await callback.message.edit_text(support_msg, reply_markup=markup)
    await callback.answer()

@dp.message(F.text.startswith("/ask "))
async def handle_support_message(message: types.Message):
    question = message.text.replace("/ask ", "", 1)
    telegram_id = str(message.from_user.id)
    
    supabase.table("messages").insert({
        "telegram_id": telegram_id,
        "direction": "inbound",
        "message": question,
        "message_type": "text"
    }).execute()
    
    await message.answer("✅ Your message has been received.\n\nOur support team will review it and reply when possible.")

@dp.callback_query(F.data == "menu_reviews")
async def show_reviews(callback: types.CallbackQuery):
    reviews_res = supabase.table("reviews").select("*").eq("active", True).limit(3).execute()
    
    if not reviews_res.data:
        msg = "⭐ No reviews available yet."
    else:
        msg = "⭐ Gautam Trading Reviews\n\nHere are some experiences shared by our users.\n\n"
        for r in reviews_res.data:
            msg += f"**{r.get('title')}**\n{r.get('content')}\n\n"
        msg += "⚠️ User experiences are individual and do not guarantee future results."
        
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔗 Get Started", callback_data="menu_affiliate")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="menu_back")]
    ])
    await callback.message.edit_text(msg, reply_markup=markup)
    await callback.answer()

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    telegram_id = str(message.from_user.id)
    admin_ids = os.getenv("ADMIN_TELEGRAM_IDS", "").split(",")
    
    if telegram_id not in admin_ids:
        return
        
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 View Stats", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")]
    ])
    await message.answer("🔒 **Admin Dashboard**\n\nSelect an option below:", reply_markup=markup, parse_mode="Markdown")

@dp.callback_query(F.data == "admin_stats")
async def admin_stats(callback: types.CallbackQuery):
    telegram_id = str(callback.from_user.id)
    if telegram_id not in os.getenv("ADMIN_TELEGRAM_IDS", "").split(","):
        return

    users_res = supabase.table("users").select("id", count="exact").execute()
    clicks_res = supabase.table("affiliate_clicks").select("id", count="exact").execute()
    
    total_users = users_res.count if hasattr(users_res, 'count') else 0
    total_clicks = clicks_res.count if hasattr(clicks_res, 'count') else 0
    
    stats_msg = (
        "📈 **Gautam Trading Stats**\n\n"
        f"👥 Total Users: {total_users}\n"
        f"🔗 Total Affiliate Clicks: {total_clicks}\n"
    )
    
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_back")]
    ])
    await callback.message.edit_text(stats_msg, reply_markup=markup, parse_mode="Markdown")
    await callback.answer()

@dp.callback_query(F.data == "admin_back")
async def admin_back(callback: types.CallbackQuery):
    markup = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📈 View Stats", callback_data="admin_stats")],
        [InlineKeyboardButton(text="📢 Broadcast", callback_data="admin_broadcast")]
    ])
    await callback.message.edit_text("🔒 **Admin Dashboard**\n\nSelect an option below:", reply_markup=markup, parse_mode="Markdown")
    await callback.answer()

from aiogram.fsm.state import State, StatesGroup

class BroadcastState(StatesGroup):
    waiting_for_message = State()

@dp.callback_query(F.data == "admin_broadcast")
async def admin_broadcast(callback: types.CallbackQuery, state: FSMContext):
    telegram_id = str(callback.from_user.id)
    if telegram_id not in os.getenv("ADMIN_TELEGRAM_IDS", "").split(","):
        return
        
    await state.set_state(BroadcastState.waiting_for_message)
    await callback.message.edit_text("📢 **Broadcast Mode**\n\nPlease send the message you want to broadcast to all users. (Or type /cancel to abort)", parse_mode="Markdown")
    await callback.answer()

@dp.message(BroadcastState.waiting_for_message)
async def process_broadcast(message: types.Message, state: FSMContext):
    if message.text == "/cancel":
        await state.clear()
        await message.answer("Broadcast cancelled.")
        return
        
    await message.answer("⏳ Sending broadcast...")
    await state.clear()
    
    # Get all users
    users_res = supabase.table("users").select("telegram_id").execute()
    users = users_res.data
    
    success = 0
    failed = 0
    
    for u in users:
        try:
            await bot.send_message(chat_id=u["telegram_id"], text=message.text)
            success += 1
        except Exception:
            failed += 1
            
    # Save broadcast stats
    supabase.table("broadcasts").insert({
        "message": message.text,
        "status": "completed",
        "total_users": len(users),
        "successful": success,
        "failed": failed
    }).execute()
    
    await message.answer(f"✅ **Broadcast Complete!**\n\nSuccessful: {success}\nFailed: {failed}", parse_mode="Markdown")

async def main():
    print("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
