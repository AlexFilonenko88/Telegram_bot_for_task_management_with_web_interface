import asyncio
import logging
import os

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import WebhookInfo

import config
from handlers import add_task, common, tasks, teams, categories, tags


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()

    dp.include_router(common.router)
    dp.include_router(tasks.router)
    dp.include_router(add_task.router)
    dp.include_router(teams.router)
    dp.include_router(categories.router)
    dp.include_router(tags.router)

    # Check if webhook mode is enabled
    use_webhook = os.getenv("USE_WEBHOOK", "false").lower() == "true"
    webhook_url = os.getenv("WEBHOOK_URL", "")

    if use_webhook and webhook_url:
        # Webhook mode
        logging.info(f"Starting bot in webhook mode: {webhook_url}")
        await bot.set_webhook(
            url=f"{webhook_url}/webhook",
            drop_pending_updates=True
        )
        # Start webhook server (this is a simplified version)
        # In production, you'd use a proper ASGI server like uvicorn
        # For now, we'll use polling as fallback
        logging.warning("Webhook mode enabled but not fully implemented. Falling back to polling.")
        await dp.start_polling(bot)
    else:
        # Polling mode (default)
        logging.info("Starting bot in polling mode")
        await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
