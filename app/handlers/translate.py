from aiogram import Router, F
from aiogram.types import CallbackQuery, Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.keyboards.main_menu import get_back_menu
from app.services.ai_service import translate_text
from app.services.rate_limit import check_rate_limit
from app.database.database import async_session
from app.database.repositories import increment_user_request, log_usage

router = Router()

class TranslateStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_language = State()
    waiting_for_custom_language = State()

def get_languages_menu():
    langs = ["English", "Tamil", "Hindi", "Malayalam", "Telugu", "Kannada", "Spanish", "French"]
    kb = []
    for i in range(0, len(langs), 2):
        kb.append([
            InlineKeyboardButton(text=langs[i], callback_data=f"lang_{langs[i]}"),
            InlineKeyboardButton(text=langs[i+1], callback_data=f"lang_{langs[i+1]}")
        ])
    kb.append([InlineKeyboardButton(text="Other Language", callback_data="lang_other")])
    kb.append([InlineKeyboardButton(text="🏠 Main Menu", callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=kb)

@router.callback_query(F.data == "feature_translate")
async def translate_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(TranslateStates.waiting_for_text)
    await callback.message.edit_text("🌍 Send the text you want translated.", reply_markup=get_back_menu())
    await callback.answer()

@router.message(TranslateStates.waiting_for_text)
async def process_translate_text(message: Message, state: FSMContext):
    await state.update_data(text_to_translate=message.text)
    await state.set_state(TranslateStates.waiting_for_language)
    await message.answer("Choose the target language:", reply_markup=get_languages_menu())

@router.callback_query(TranslateStates.waiting_for_language, F.data.startswith("lang_"))
async def process_translate_lang(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split("_")[1]
    if lang == "other":
        await state.set_state(TranslateStates.waiting_for_custom_language)
        await callback.message.edit_text("Type the language you want to translate to:", reply_markup=get_back_menu())
        return
        
    await _do_translation(callback.message, state, callback.from_user.id, lang)
    await callback.answer()

@router.message(TranslateStates.waiting_for_custom_language)
async def process_custom_lang(message: Message, state: FSMContext):
    await _do_translation(message, state, message.from_user.id, message.text)

async def _do_translation(message, state: FSMContext, user_id: int, language: str):
    data = await state.get_data()
    text = data.get("text_to_translate")
    
    if not await check_rate_limit(user_id):
        if isinstance(message, Message):
            await message.answer("⏳ You've reached the current usage limit.")
        else:
            await message.edit_text("⏳ You've reached the current usage limit.")
        return
        
    await state.clear()
    
    if isinstance(message, Message):
        wait_msg = await message.answer(f"🤔 Translating to {language}...")
    else:
        await message.edit_text(f"🤔 Translating to {language}...")
        wait_msg = message
        
    response = await translate_text(text, language)
    
    async with async_session() as session:
        await increment_user_request(session, user_id)
        await log_usage(session, user_id, "translate")
        
    await wait_msg.edit_text(response, reply_markup=get_back_menu())
