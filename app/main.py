import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from aiogram.types import Update
from app.config import settings
from app.bot import bot, dp, setup_bot
from app.database.database import init_db

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB
    await init_db()
    await setup_bot()
    
    if settings.webhook_url:
        webhook_info = await bot.get_webhook_info()
        if webhook_info.url != settings.webhook_url:
            await bot.set_webhook(url=settings.webhook_url, secret_token=settings.webhook_secret)
        logging.info(f"Webhook set to {settings.webhook_url}")
    else:
        # For local testing via polling
        import asyncio
        await bot.delete_webhook(drop_pending_updates=True)
        asyncio.create_task(dp.start_polling(bot))
        logging.info("Started polling mode")
        
    yield
    
    if settings.webhook_url:
        await bot.delete_webhook()
    await bot.session.close()

app = FastAPI(lifespan=lifespan)

@app.post("/webhook")
async def webhook_handler(request: Request):
    secret_token = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if settings.webhook_secret and secret_token != settings.webhook_secret:
        return {"status": "unauthorized"}
        
    update_data = await request.json()
    update = Update(**update_data)
    await dp.feed_update(bot, update)
    return {"status": "ok"}

@app.get("/health")
async def health_check():
    return {"status": "ok"}
