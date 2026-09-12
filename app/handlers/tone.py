from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.keyboards.main_menu import get_back_menu
from app.services.ai_service import change_tone
from app.services.rate_limit import check_rate_limit
from app.database.database import async_session
from app.database.repositories import increment_user_request, log_usage

router = Router()

class ToneStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_tone = State()

def get_tones_menu():
    tones = ["Professional", "Friendly", "Casual", "Formal", "Confident", "Persuasive", "Polite", "Concise"]
    kb = []
    for i in range(0, len(tones), 2):
        kb.append([
            InlineKeyboardButton(text=tones[i], callback_data=f"tone_{tones[i]}"),
            InlineKeyboardButton(text=tones[i+1], callback_data=f"tone_{tones[i+1]}")
        ])
    kb.append([InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

@router.callback_query(F.data == "feature_tone")
async def tone_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(ToneStates.waiting_for_text)
    await callback.message.edit_text("🎨 Send me the text you want to change the tone for.", reply_markup=get_back_menu())
    await callback.answer()

@router.message(ToneStates.waiting_for_text)
async def process_tone_text(message: Message, state: FSMContext):
    await state.update_data(text_to_tone=message.text)
    await state.set_state(ToneStates.waiting_for_tone)
    await message.answer("Choose the tone:", reply_markup=get_tones_menu())

@router.callback_query(ToneStates.waiting_for_tone, F.data.startswith("tone_"))
async def process_tone_style(callback: CallbackQuery, state: FSMContext):
    tone = callback.data.split("_")[1]
    data = await state.get_data()
    text = data.get("text_to_tone")
    
    if not await check_rate_limit(callback.from_user.id):
        await callback.message.edit_text("⏳ You've reached the current usage limit. Please try again later.", reply_markup=get_back_menu())
        return
        
    await state.clear()
    await callback.message.edit_text(f"🤔 Changing tone to {tone}...")
    
    response = await change_tone(text, tone)
    
    async with async_session() as session:
        await increment_user_request(session, callback.from_user.id)
        await log_usage(session, callback.from_user.id, "tone")
        
    await callback.message.edit_text(response, reply_markup=get_back_menu())
    await callback.answer()
