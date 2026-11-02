"""CRUD-операции для категорий задач."""

from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Category
from app.schemas.task import CategoryCreate


def get_category(db: Session, category_id: int) -> Optional[Category]:
    """Вернуть категорию по первичному ключу или None."""
    return db.query(Category).filter(Category.id == category_id).first()


def get_categories_by_user(
    db: Session,
    user_id: int,
    *,
    limit: Optional[int] = None,
    offset: int = 0,
) -> List[Category]:
    """Категории пользователя.

    Args:
        db: сессия SQLAlchemy.
        user_id: владелец категорий.
        limit: размер страницы; None — все.
        offset: смещение первой записи.

    Returns:
        Список категорий.
    """
    query = db.query(Category).filter(Category.user_id == user_id)
    if limit is not None:
        query = query.limit(limit).offset(offset)
    return query.all()


def count_categories_by_user(db: Session, user_id: int) -> int:
    """Общее число категорий пользователя — для поля total в пагинации."""
    return db.query(Category).filter(Category.user_id == user_id).count()


def create_category(db: Session, category: CategoryCreate) -> Category:
    """Создать категорию.

    Args:
        db: сессия SQLAlchemy.
        category: валидированные данные (имя + владелец).

    Returns:
        Созданная категория с заполненным id.
    """
    db_category = Category(name=category.name, user_id=category.user_id)
    db.add(db_category)
    db.commit()
    db.refresh(db_category)
    return db_category


def delete_category(db: Session, category_id: int) -> bool:
    """Удалить категорию.

    Returns:
        True — удалена, False — не найдена.
    """
    db_category = get_category(db, category_id)
    if not db_category:
        return False

    db.delete(db_category)
    db.commit()
    return True
