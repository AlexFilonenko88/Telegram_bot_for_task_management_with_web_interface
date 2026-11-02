"""CRUD-слой: операции с БД, сгруппированные по сущностям (Single Responsibility).

Все запросы строятся через SQLAlchemy ORM — параметры всегда связываются
движком (параметризованные запросы), конкатенация SQL-строк не используется.
"""

from app.crud.task import (
    get_task,
    get_tasks_by_user,
    count_tasks_by_user,
    create_task,
    update_task,
    delete_task,
)
from app.crud.user import (
    get_user_by_telegram_id,
    create_user,
    get_or_create_user,
)
from app.crud.team import (
    get_team_by_name,
    create_team,
    add_user_to_team,
    get_team_tasks,
    count_team_tasks,
)
from app.crud.category import (
    get_category,
    get_categories_by_user,
    count_categories_by_user,
    create_category,
    delete_category,
)
from app.crud.tag import (
    get_tag,
    get_tags_by_user,
    count_tags_by_user,
    create_tag,
    delete_tag,
)
from app.crud.stats import get_weekly_stats, get_team_weekly_stats
from app.crud.reminders import get_tasks_with_upcoming_deadlines, mark_reminder_sent

__all__ = [
    "get_task", "get_tasks_by_user", "count_tasks_by_user",
    "create_task", "update_task", "delete_task",
    "get_user_by_telegram_id", "create_user", "get_or_create_user",
    "get_team_by_name", "create_team", "add_user_to_team",
    "get_team_tasks", "count_team_tasks",
    "get_category", "get_categories_by_user", "count_categories_by_user",
    "create_category", "delete_category",
    "get_tag", "get_tags_by_user", "count_tags_by_user",
    "create_tag", "delete_tag",
    "get_weekly_stats", "get_team_weekly_stats",
    "get_tasks_with_upcoming_deadlines", "mark_reminder_sent",
]
