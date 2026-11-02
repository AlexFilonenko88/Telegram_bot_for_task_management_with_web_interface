"""CRUD-операции для пользователей."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models import User
from app.schemas.user import UserCreate


def get_user_by_telegram_id(db: Session, telegram_id: int) -> Optional[User]:
    """Вернуть пользователя по telegram_id или None."""
    return db.query(User).filter(User.telegram_id == telegram_id).first()


def create_user(db: Session, user: UserCreate) -> User:
    """Создать пользователя.

    Args:
        db: сессия SQLAlchemy.
        user: валидированные данные (telegram_id, username, first_name).

    Returns:
        Созданный пользователь с заполненным id.
    """
    db_user = User(
        telegram_id=user.telegram_id,
        username=user.username,
        first_name=user.first_name,
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_or_create_user(db: Session, user: UserCreate) -> User:
    """Идемпотентно вернуть пользователя по telegram_id, создав при необходимости."""
    db_user = get_user_by_telegram_id(db, user.telegram_id)
    if db_user:
        return db_user
    return create_user(db, user)
