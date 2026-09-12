from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.keyboards.main_menu import get_back_menu
from app.services.ai_service import summarize_text
from app.services.rate_limit import check_rate_limit
from app.database.database import async_session
from app.database.repositories import increment_user_request, log_usage

router = Router()

class SummarizeStates(StatesGroup):
    waiting_for_text = State()

@router.callback_query(F.data == "feature_summarize")
async def summarize_start(callback: CallbackQuery, state: FSMContext):
    await state.set_state(SummarizeStates.waiting_for_text)
    await callback.message.edit_text("📚 Send the text you want me to summarize.", reply_markup=get_back_menu())
    await callback.answer()

@router.message(SummarizeStates.waiting_for_text)
async def process_summarize(message: Message, state: FSMContext):
    if not await check_rate_limit(message.from_user.id):
        await message.answer("⏳ You've reached the current usage limit. Please try again later.")
        return
        
    await state.clear()
    wait_msg = await message.answer("🤔 Summarizing...")
    
    response = await summarize_text(message.text)
    
    async with async_session() as session:
        await increment_user_request(session, message.from_user.id)
        await log_usage(session, message.from_user.id, "summarize")
        
    await wait_msg.edit_text(response, reply_markup=get_back_menu())
