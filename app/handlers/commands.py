from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.keyboards.main_menu import get_back_menu
from app.handlers.ask import AskStates
from app.handlers.summarize import SummarizeStates
from app.handlers.rewrite import RewriteStates
from app.handlers.grammar import GrammarStates
from app.handlers.generate import GenerateStates
from app.handlers.translate import TranslateStates
from app.handlers.tone import ToneStates

router = Router()

@router.message(Command("ask"))
async def cmd_ask(message: Message, state: FSMContext):
    await state.set_state(AskStates.waiting_for_question)
    await message.answer("💬 What would you like to ask?", reply_markup=get_back_menu())

@router.message(Command("summarize"))
async def cmd_summarize(message: Message, state: FSMContext):
    await state.set_state(SummarizeStates.waiting_for_text)
    await message.answer("📚 Send the text you want me to summarize.", reply_markup=get_back_menu())

@router.message(Command("rewrite"))
async def cmd_rewrite(message: Message, state: FSMContext):
    await state.set_state(RewriteStates.waiting_for_text)
    await message.answer("📝 Send me the text you want rewritten.", reply_markup=get_back_menu())

@router.message(Command("grammar"))
async def cmd_grammar(message: Message, state: FSMContext):
    await state.set_state(GrammarStates.waiting_for_text)
    await message.answer("✅ Send me your text and I'll correct grammar, spelling, punctuation, and clarity.", reply_markup=get_back_menu())

@router.message(Command("generate"))
async def cmd_generate(message: Message, state: FSMContext):
    await state.set_state(GenerateStates.waiting_for_prompt)
    await message.answer("✍️ What would you like me to create? (e.g. Email to boss, Instagram caption)", reply_markup=get_back_menu())

@router.message(Command("translate"))
async def cmd_translate(message: Message, state: FSMContext):
    await state.set_state(TranslateStates.waiting_for_text)
    await message.answer("🌍 Send the text you want translated.", reply_markup=get_back_menu())

@router.message(Command("tone"))
async def cmd_tone(message: Message, state: FSMContext):
    await state.set_state(ToneStates.waiting_for_text)
    await message.answer("🎨 Send me the text you want to change the tone for.", reply_markup=get_back_menu())