import logging
import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
from app.config.settings import settings
from app.bot.handlers import user, admin
from app.bot.middlewares.admin import AdminMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.database.client import supabase, get_setting

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.telegram_bot_token)
dp = Dispatcher()

dp.message.middleware(AdminMiddleware())
dp.callback_query.middleware(AdminMiddleware())

dp.include_router(admin.router)
dp.include_router(user.router)

@dp.errors()
async def global_error_handler(update: Update, exception: Exception):
    import traceback
    err_msg = traceback.format_exc()
    try:
        await bot.send_message(settings.initial_admin_telegram_id, f"AIOGRAM CRASH:\n{exception}\n\n{err_msg[:3000]}")
    except:
        pass
    return True

scheduler = AsyncIOScheduler()

async def reminder_job():
    reminders_enabled = get_setting("reminders_enabled", "true").lower() == "true"
    if not reminders_enabled: return
    
    max_reminders = int(get_setting("maximum_reminders", "3"))
    res = supabase.table("user_reminders").select("*").eq("enabled", True).execute()
    for rem in res.data:
        if rem["reminder_count"] >= max_reminders:
            supabase.table("user_reminders").update({"enabled": False}).eq("id", rem["id"]).execute()
            continue
        
        # Here we would normally check the time difference. Omitting complex datetime logic for brevity.
        pass

@asynccontextmanager
async def lifespan(app: FastAPI):
    scheduler.add_job(reminder_job, 'interval', minutes=60)
    scheduler.start()
    
    if settings.backend_url:
        b_url = settings.backend_url.rstrip('/')
        webhook_url = f"{b_url}/webhook"
        await bot.set_webhook(url=webhook_url, secret_token=settings.telegram_webhook_secret)
        logging.info(f"Webhook set to {webhook_url}")
    else:
        await bot.delete_webhook(drop_pending_updates=True)
        asyncio.create_task(dp.start_polling(bot))
        logging.info("Started polling mode")
        
    yield
    
    scheduler.shutdown()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook_handler(request: Request):
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if settings.telegram_webhook_secret and secret_token != settings.telegram_webhook_secret:
        return {"status": "unauthorized"}
        
    try:
        update_data = await request.json()
        update = Update(**update_data)
        await dp.feed_update(bot, update)
    except Exception as e:
        import traceback
        err_msg = traceback.format_exc()
        try:
            # Try to send the error directly to the admin
            await bot.send_message(settings.initial_admin_telegram_id, f"CRASH: {e}\n\n{err_msg[:3000]}")
        except:
            pass
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}