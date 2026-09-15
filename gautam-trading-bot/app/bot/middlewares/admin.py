from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
from app.database.client import supabase

class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]], event: Message|CallbackQuery, data: Dict[str, Any]) -> Any:
        user_id = event.from_user.id
        res = supabase.table("admins").select("enabled").eq("telegram_id", user_id).execute()
        is_admin = False
        if res.data and res.data[0].get("enabled") == True:
            is_admin = True
        
        data['is_admin'] = is_admin
        return await handler(event, data)