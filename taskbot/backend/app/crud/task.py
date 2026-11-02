"""CRUD-операции для задач."""

from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Task, Tag
from app.schemas.task import TaskCreate, TaskUpdate


def get_task(db: Session, task_id: int) -> Optional[Task]:
    """Вернуть задачу по первичному ключу или None, если не найдена."""
    return db.query(Task).filter(Task.id == task_id).first()


def get_tasks_by_user(
    db: Session,
    user_id: int,
    *,
    limit: Optional[int] = None,
    offset: int = 0,
    is_done: Optional[bool] = None,
) -> List[Task]:
    """Задачи пользователя, упорядоченные по id.

    Args:
        db: сессия SQLAlchemy.
        user_id: владелец задач.
        limit: размер страницы; None — вернуть все (внутренние расчёты статистики).
        offset: смещение первой записи (применяется только с limit).
        is_done: фильтр по статусу; None — без фильтра.

    Returns:
        Список задач (возможно, пустой).
    """
    query = db.query(Task).filter(Task.user_id == user_id)
    if is_done is not None:
        query = query.filter(Task.is_done == is_done)
    if limit is not None:
        query = query.limit(limit).offset(offset)
    return query.all()


def count_tasks_by_user(
    db: Session, user_id: int, *, is_done: Optional[bool] = None
) -> int:
    """Число задач пользователя (с опциональным фильтром) — для пагинации."""
    query = db.query(Task).filter(Task.user_id == user_id)
    if is_done is not None:
        query = query.filter(Task.is_done == is_done)
    return query.count()


def create_task(db: Session, task: TaskCreate) -> Task:
    """Создать задачу и привязать теги, если они переданы.

    Args:
        db: сессия SQLAlchemy.
        task: валидированные данные создания (Pydantic).

    Returns:
        Созданная задача с заполненным id.
    """
    db_task = Task(
        title=task.title,
        description=task.description,
        user_id=task.user_id,
        priority=task.priority,
        deadline=task.deadline,
        category_id=task.category_id,
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)

    if task.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(task.tag_ids)).all()
        db_task.tags = tags
        db.commit()
        db.refresh(db_task)

    return db_task


def update_task(db: Session, task_id: int, task_update: TaskUpdate) -> Optional[Task]:
    """Частично обновить задачу (exclude_unset).

    При установке is_done=True фиксирует время выполнения в completed_at.
    Args:
        db: сессия SQLAlchemy.
        task_id: идентификатор задачи.
        task_update: изменяемые поля.

    Returns:
        Обновлённая задача или None, если задача не найдена.
    """
    db_task = get_task(db, task_id)
    if not db_task:
        return None

    update_data = task_update.model_dump(exclude_unset=True, exclude={"tag_ids"})
    for field, value in update_data.items():
        setattr(db_task, field, value)

    if "is_done" in update_data and update_data["is_done"] and not db_task.completed_at:
        db_task.completed_at = datetime.utcnow()

    if task_update.tag_ids is not None:
        tags = db.query(Tag).filter(Tag.id.in_(task_update.tag_ids)).all()
        db_task.tags = tags

    db.commit()
    db.refresh(db_task)
    return db_task


def delete_task(db: Session, task_id: int) -> bool:
    """Удалить задачу.

    Returns:
        True — удалена, False — не найдена.
    """
    db_task = get_task(db, task_id)
    if not db_task:
        return False

    db.delete(db_task)
    db.commit()
    return True
