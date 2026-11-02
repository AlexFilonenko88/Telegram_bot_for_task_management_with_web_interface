"""CRUD-операции для команд и членства в них."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Task, Team, User
from app.schemas.user import TeamCreate


def get_team_by_name(db: Session, name: str) -> Optional[Team]:
    """Вернуть команду по имени или None."""
    return db.query(Team).filter(Team.name == name).first()


def create_team(db: Session, team: TeamCreate) -> Team:
    """Создать команду.

    Args:
        db: сессия SQLAlchemy.
        team: валидированные данные (имя команды).

    Returns:
        Созданная команда с заполненным id.
    """
    db_team = Team(name=team.name)
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


def add_user_to_team(db: Session, user_id: int, team_id: int) -> Optional[User]:
    """Записать пользователя в команду.

    Args:
        db: сессия SQLAlchemy.
        user_id: внутренний id пользователя (не telegram_id).
        team_id: id команды.

    Returns:
        Обновлённый пользователь или None, если пользователь не найден.
    """
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        return None

    db_user.team_id = team_id
    db.commit()
    db.refresh(db_user)
    return db_user


def get_team_tasks(
    db: Session,
    team_id: int,
    *,
    limit: Optional[int] = None,
    offset: int = 0,
) -> List[Task]:
    """Задачи всех участников команды.

    Args:
        db: сессия SQLAlchemy.
        team_id: id команды.
        limit: размер страницы; None — все (для статистики).
        offset: смещение первой записи.

    Returns:
        Список задач команды.
    """
    query = db.query(Task).join(User).filter(User.team_id == team_id)
    if limit is not None:
        query = query.limit(limit).offset(offset)
    return query.all()


def count_team_tasks(db: Session, team_id: int) -> int:
    """Общее число задач команды — для поля total в пагинации."""
    return db.query(Task).join(User).filter(User.team_id == team_id).count()
