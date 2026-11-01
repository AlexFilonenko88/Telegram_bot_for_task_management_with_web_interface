import logging
from fastapi import APIRouter, Request
from aiogram import Bot, Dispatcher
from aiogram.types import Update
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

# Global bot and dispatcher instances (will be set from main.py)
bot: Bot = None
dp: Dispatcher = None


def set_webhook_bot(b: Bot, d: Dispatcher):
    """Set the bot and dispatcher instances for webhook handling."""
    global bot, dp
    bot = b
    dp = d


@router.post("/webhook")
async def telegram_webhook(request: Request):
    """Handle incoming Telegram webhook updates."""
    if bot is None or dp is None:
        logger.error("Bot or dispatcher not initialized")
        return {"status": "error", "message": "Bot not initialized"}

    try:
        update = await request.json()
        telegram_update = Update(**update)
        await dp.feed_webhook_update(bot, telegram_update)
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error processing webhook update: {e}")
        return {"status": "error", "message": str(e)}


async def setup_webhook():
    """Setup webhook for the bot."""
    if bot is None:
        logger.error("Bot not initialized")
        return

    webhook_url = os.getenv("WEBHOOK_URL", "")
    if webhook_url:
        try:
            await bot.set_webhook(
                url=f"{webhook_url}/webhook",
                drop_pending_updates=True
            )
            logger.info(f"Webhook set to: {webhook_url}/webhook")
        except Exception as e:
            logger.error(f"Failed to set webhook: {e}")


async def delete_webhook():
    """Delete webhook and return to polling mode."""
    if bot is None:
        logger.error("Bot not initialized")
        return

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        logger.info("Webhook deleted")
    except Exception as e:
        logger.error(f"Failed to delete webhook: {e}")
