from aiogram import Bot, Dispatcher
from app.config import settings
from app.handlers import start, ask, summarize, rewrite, grammar, generate, translate, tone, more_tools

bot = Bot(token=settings.bot_token)
dp = Dispatcher()

# Register handlers
dp.include_router(start.router)
dp.include_router(ask.router)
dp.include_router(summarize.router)
dp.include_router(rewrite.router)
dp.include_router(grammar.router)
dp.include_router(generate.router)
dp.include_router(translate.router)
dp.include_router(tone.router)
dp.include_router(more_tools.router)
# Include other handlers as needed...

async def setup_bot():
    pass
