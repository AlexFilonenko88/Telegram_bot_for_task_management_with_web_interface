import asyncio
import logging
import os
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app import crud
import httpx

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
BOT_TOKEN = os.getenv("BOT_TOKEN")


async def send_telegram_message(telegram_id: int, message: str):
    """Send a message to a Telegram user via the bot API."""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                json={
                    "chat_id": telegram_id,
                    "text": message,
                    "parse_mode": "HTML"
                }
            )
            response.raise_for_status()
            logger.info(f"Message sent to user {telegram_id}")
    except Exception as e:
        logger.error(f"Failed to send message to user {telegram_id}: {e}")


async def check_and_send_reminders():
    """Check for tasks with upcoming deadlines and send reminders."""
    db = SessionLocal()
    try:
        # Get tasks with deadlines in the next 24 hours
        tasks = crud.get_tasks_with_upcoming_deadlines(db, hours_ahead=24)

        for task in tasks:
            # Format deadline for display
            deadline_str = task.deadline.strftime("%Y-%m-%d %H:%M")
            priority_emoji = {
                "high": "🔴",
                "medium": "🟡",
                "low": "🟢"
            }.get(task.priority, "")

            message = (
                f"⏰ <b>Напоминание о задаче!</b>\n\n"
                f"{priority_emoji} <b>{task.title}</b>\n"
                f"📅 Дедлайн: {deadline_str}\n"
                f"📝 {task.description if task.description else 'Без описания'}\n\n"
                f"Не забудьте выполнить задачу вовремя!"
            )

            # Send reminder to user
            await send_telegram_message(task.user.telegram_id, message)

            # Mark reminder as sent
            crud.mark_reminder_sent(db, task.id)

        if tasks:
            logger.info(f"Sent {len(tasks)} reminders")
    except Exception as e:
        logger.error(f"Error in check_and_send_reminders: {e}")
    finally:
        db.close()


def start_scheduler():
    """Start the APScheduler for reminders."""
    scheduler.add_job(
        check_and_send_reminders,
        'interval',
        minutes=30,  # Check every 30 minutes
        id='reminder_checker',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Reminder scheduler started")


def stop_scheduler():
    """Stop the APScheduler."""
    scheduler.shutdown()
    logger.info("Reminder scheduler stopped")
