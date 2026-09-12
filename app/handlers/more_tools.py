from aiogram import Router, F
from aiogram.types import CallbackQuery
from app.keyboards.main_menu import get_more_tools_menu
from app.handlers.generate import GenerateStates
from app.handlers.rewrite import RewriteStates
from aiogram.fsm.context import FSMContext

router = Router()

@router.callback_query(F.data == "feature_more")
async def more_tools_menu(callback: CallbackQuery):
    await callback.message.edit_text("💡 Choose an extra tool:", reply_markup=get_more_tools_menu())
    await callback.answer()

@router.callback_query(F.data == "feature_generate_email")
async def generate_email(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GenerateStates.waiting_for_prompt)
    await callback.message.edit_text("📧 What should the email be about? (e.g. Asking my boss for a raise)")
    await callback.answer()

@router.callback_query(F.data == "feature_generate_social")
async def generate_social(callback: CallbackQuery, state: FSMContext):
    await state.set_state(GenerateStates.waiting_for_prompt)
    await callback.message.edit_text("📱 What is the social media post about? (e.g. My new coffee shop opening)")
    await callback.answer()

@router.callback_query(F.data == "feature_rewrite_shorter")
async def rewrite_shorter(callback: CallbackQuery, state: FSMContext):
    await state.set_state(RewriteStates.waiting_for_style)
    await state.update_data(text_to_rewrite="Make this shorter") 
    # Just reusing the rewrite text state for simplicity in routing
    await callback.message.edit_text("🔤 Send me the text you want to make shorter:")
    await state.set_state(RewriteStates.waiting_for_text) # wait actually rewrite expects state update first
    await callback.answer()

@router.callback_query(F.data == "feature_rewrite_longer")
async def rewrite_longer(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("📖 Send me the text you want to expand:")
    await state.set_state(RewriteStates.waiting_for_text)
    await callback.answer()
