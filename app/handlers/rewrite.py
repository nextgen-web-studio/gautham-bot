from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.keyboards.main_menu import get_back_menu, get_rewrite_styles
from app.services.ai_service import rewrite_text
from app.services.rate_limit import check_rate_limit
from app.database.database import async_session
from app.database.repositories import increment_user_request, log_usage

router = Router()

class RewriteStates(StatesGroup):
    waiting_for_text = State()
    waiting_for_style = State()

@router.callback_query(F.data == "feature_rewrite")
async def rewrite_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RewriteStates.waiting_for_text)
    await callback.message.edit_text("📝 Send me the text you want rewritten.", reply_markup=get_back_menu())
    await callback.answer()

@router.message(RewriteStates.waiting_for_text)
async def process_rewrite_text(message: Message, state: FSMContext):
    await state.update_data(text_to_rewrite=message.text)
    await state.set_state(RewriteStates.waiting_for_style)
    await message.answer("Please choose a style:", reply_markup=get_rewrite_styles())

@router.callback_query(RewriteStates.waiting_for_style, F.data.startswith("style_"))
async def process_rewrite_style(callback: CallbackQuery, state: FSMContext):
    style = callback.data.split("_")[1]
    data = await state.get_data()
    text = data.get("text_to_rewrite")
    
    if not await check_rate_limit(callback.from_user.id):
        await callback.message.edit_text("⏳ You've reached the current usage limit. Please try again later.", reply_markup=get_back_menu())
        return
        
    await state.clear()
    await callback.message.edit_text(f"🤔 Rewriting in {style} style...")
    
    response = await rewrite_text(text, style)
    
    async with async_session() as session:
        await increment_user_request(session, callback.from_user.id)
        await log_usage(session, callback.from_user.id, "rewrite")
        
    await callback.message.edit_text(response, reply_markup=get_back_menu())
    await callback.answer()
