from aiogram import Bot, Dispatcher
from app.config import settings
from app.handlers import start, ask, summarize, rewrite, grammar, generate, translate, tone, more_tools, commands
from aiogram.types import BotCommand

bot = Bot(token=settings.bot_token)
dp = Dispatcher()

# Register handlers
dp.include_router(start.router)
dp.include_router(commands.router)
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
    await bot.set_my_commands([
        BotCommand(command="start", description="Start the bot and show main menu"),
        BotCommand(command="ask", description="Ask the AI a question"),
        BotCommand(command="summarize", description="Summarize text"),
        BotCommand(command="rewrite", description="Rewrite text"),
        BotCommand(command="grammar", description="Correct grammar and spelling"),
        BotCommand(command="generate", description="Generate content from a prompt"),
        BotCommand(command="translate", description="Translate text"),
        BotCommand(command="tone", description="Change the tone of text")
    ])
