"""CRUD-операции для тегов задач."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Tag
from app.schemas.task import TagCreate


def get_tag(db: Session, tag_id: int) -> Optional[Tag]:
    """Вернуть тег по первичному ключу или None."""
    return db.query(Tag).filter(Tag.id == tag_id).first()


def get_tags_by_user(
    db: Session,
    user_id: int,
    *,
    limit: Optional[int] = None,
    offset: int = 0,
) -> List[Tag]:
    """Теги пользователя.

    Args:
        db: сессия SQLAlchemy.
        user_id: владелец тегов.
        limit: размер страницы; None — все.
        offset: смещение первой записи.

    Returns:
        Список тегов.
    """
    query = db.query(Tag).filter(Tag.user_id == user_id)
    if limit is not None:
        query = query.limit(limit).offset(offset)
    return query.all()


def count_tags_by_user(db: Session, user_id: int) -> int:
    """Общее число тегов пользователя — для поля total в пагинации."""
    return db.query(Tag).filter(Tag.user_id == user_id).count()


def create_tag(db: Session, tag: TagCreate) -> Tag:
    """Создать тег.

    Args:
        db: сессия SQLAlchemy.
        tag: валидированные данные (имя + владелец).

    Returns:
        Созданный тег с заполненным id.
    """
    db_tag = Tag(name=tag.name, user_id=tag.user_id)
    db.add(db_tag)
    db.commit()
    db.refresh(db_tag)
    return db_tag


def delete_tag(db: Session, tag_id: int) -> bool:
    """Удалить тег.

    Returns:
        True — удалён, False — не найден.
    """
    db_tag = get_tag(db, tag_id)
    if not db_tag:
        return False

    db.delete(db_tag)
    db.commit()
    return True
