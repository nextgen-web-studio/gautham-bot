from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from app.database.client import supabase

router = Router()

class ProofStates(StatesGroup):
    waiting_for_media = State()
    waiting_for_caption = State()

def proof_menu_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Add New Proof", callback_data="admin_add_proof")],
        [InlineKeyboardButton(text="🗑 Clear All Proofs", callback_data="admin_clear_proofs")],
        [InlineKeyboardButton(text="⬅️ Back", callback_data="admin_main")]
    ])

@router.callback_query(F.data == "admin_proof")
async def proof_menu(callback: CallbackQuery, is_admin: bool):
    if not is_admin: return
    proofs = supabase.table("proof_content").select("id", count="exact").execute()
    count = proofs.count or 0
    await callback.message.edit_text(f"📸 PROOF / REVIEWS\n\nCurrently active proofs: {count}\n\nWhat would you like to do?", reply_markup=proof_menu_kb())
    await callback.answer()

@router.callback_query(F.data == "admin_clear_proofs")
async def clear_proofs(callback: CallbackQuery, is_admin: bool):
    if not is_admin: return
    supabase.table("proof_content").delete().neq("id", 0).execute()
    await callback.answer("✅ All proofs cleared!", show_alert=True)
    await proof_menu(callback, is_admin)

@router.callback_query(F.data == "admin_add_proof")
async def add_proof(callback: CallbackQuery, is_admin: bool, state: FSMContext):
    if not is_admin: return
    await state.set_state(ProofStates.waiting_for_media)
    await callback.message.edit_text("📸 Please send me the image or video for the proof (or send /cancel to abort):")
    await callback.answer()

@router.message(ProofStates.waiting_for_media, F.photo | F.video)
async def process_proof_media(message: Message, is_admin: bool, state: FSMContext):
    if not is_admin: return
    file_id = message.photo[-1].file_id if message.photo else message.video.file_id
    content_type = "image" if message.photo else "video"
    
    await state.update_data(file_id=file_id, content_type=content_type)
    await state.set_state(ProofStates.waiting_for_caption)
    await message.answer("📝 Great! Now send me the caption for this proof (or send 'skip' for no caption):")

@router.message(ProofStates.waiting_for_caption)
async def process_proof_caption(message: Message, is_admin: bool, state: FSMContext):
    if not is_admin: return
    data = await state.get_data()
    caption = message.text if message.text.lower() != "skip" else ""
    
    supabase.table("proof_content").insert({
        "file_id": data["file_id"],
        "content_type": data["content_type"],
        "caption": caption,
        "enabled": True,
        "sort_order": 0
    }).execute()
    
    await state.clear()
    await message.answer("✅ Proof added successfully!")