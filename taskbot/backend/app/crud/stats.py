"""Статистика выполнения задач за неделю (пользователь и команда)."""

from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session

from app.crud.task import get_tasks_by_user
from app.crud.team import get_team_tasks
from app.models import Task


def _build_weekly_stats(tasks: List[Task]) -> dict:
    """Собрать сводку по списку задач: разбивку по дням за 7 дней и итоги.

    Внутренний хелпер, общий для пользовательской и командной статистики (DRY).
    Поведение сохранено: «выполнено за день» считается по created_at задачи.
    """
    today = datetime.now().date()
    week_ago = today - timedelta(days=6)

    daily_stats = []
    for i in range(7):
        day = week_ago + timedelta(days=i)
        day_start = datetime.combine(day, datetime.min.time())
        day_end = datetime.combine(day, datetime.max.time())

        completed_on_day = sum(
            1 for task in tasks
            if task.is_done and day_start <= task.created_at <= day_end
        )

        daily_stats.append({
            "date": day.strftime("%Y-%m-%d"),
            "day_name": day.strftime("%A"),
            "completed": completed_on_day,
        })

    total = len(tasks)
    done = len([t for t in tasks if t.is_done])
    active = total - done
    percentage = (done / total * 100) if total > 0 else 0

    return {
        "total": total,
        "done": done,
        "active": active,
        "percentage": round(percentage, 1),
        "daily_stats": daily_stats,
    }


def get_weekly_stats(db: Session, user_id: int) -> dict:
    """Статистика выполнения задач пользователя за последние 7 дней.

    Args:
        db: сессия SQLAlchemy.
        user_id: владелец задач.

    Returns:
        Словарь: total, done, active, percentage, daily_stats (7 записей).
    """
    tasks = get_tasks_by_user(db, user_id)
    return _build_weekly_stats(tasks)


def get_team_weekly_stats(db: Session, team_id: int) -> dict:
    """Статистика выполнения задач команды за последние 7 дней.

    Args:
        db: сессия SQLAlchemy.
        team_id: id команды.

    Returns:
        Словарь: total, done, active, percentage, daily_stats (7 записей).
    """
    tasks = get_team_tasks(db, team_id)
    return _build_weekly_stats(tasks)
