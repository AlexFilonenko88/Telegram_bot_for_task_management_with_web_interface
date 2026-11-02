"""Напоминания о дедлайнах задач (используются планировщиком notifications)."""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.models import Task, User


def get_tasks_with_upcoming_deadlines(db: Session, hours_ahead: int = 24) -> List[Task]:
    """Найти незавершённые задачи с дедлайном в ближайшие N часов.

    Возвращает только задачи, по которым ещё не отправлялось напоминание.
    Args:
        db: сессия SQLAlchemy.
        hours_ahead: горизонт поиска в часах.

    Returns:
        Список задач, требующих напоминания.
    """
    now = datetime.utcnow()
    deadline_limit = now + timedelta(hours=hours_ahead)

    return db.query(Task).join(User).filter(
        Task.deadline.isnot(None),
        Task.deadline <= deadline_limit,
        Task.deadline > now,
        Task.reminder_sent == False,  # noqa: E712 — SQLAlchemy требует ==
        Task.is_done == False,        # noqa: E712
    ).all()


def mark_reminder_sent(db: Session, task_id: int) -> bool:
    """Пометить задачу как обработанную напоминанием.

    Returns:
        True — помечена, False — задача не найдена.
    """
    from app.crud.task import get_task

    db_task = get_task(db, task_id)
    if not db_task:
        return False

    db_task.reminder_sent = True
    db.commit()
    return True
