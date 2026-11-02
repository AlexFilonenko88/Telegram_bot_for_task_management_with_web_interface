"""Роутер задач: /api/tasks.

Списковые эндпоинты возвращают Page[TaskResponse] (пагинация limit/offset),
остальные — одиночные объекты. Доступ для анонимных клиентов ограничен
GET-запросами на уровне middleware (см. app/main.py).
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.deps import Pagination, paginate
from app.schemas.pagination import Page
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("", response_model=Page[TaskResponse])
def get_tasks(
    user_id: int,
    is_done: Optional[bool] = Query(None, description="Фильтр по статусу задачи"),
    pagination: Pagination = Depends(paginate),
    db: Session = Depends(get_db),
) -> Page[TaskResponse]:
    """Постраничный список задач пользователя.

    Args:
        user_id: владелец задач (query-параметр).
        is_done: опциональный фильтр по статусу (true/false).
        pagination: limit/offset из query-параметров.
        db: сессия БД (DI).

    Returns:
        Страница задач: items, total, limit, offset.
    """
    tasks = crud.get_tasks_by_user(
        db, user_id, limit=pagination.limit, offset=pagination.offset, is_done=is_done
    )
    total = crud.count_tasks_by_user(db, user_id, is_done=is_done)
    return Page(
        items=tasks, total=total, limit=pagination.limit, offset=pagination.offset
    )


@router.get("/stats/weekly")
def get_weekly_stats(user_id: int, db: Session = Depends(get_db)) -> dict:
    """Статистика выполнения задач пользователя за последние 7 дней."""
    return crud.get_weekly_stats(db, user_id)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)) -> TaskResponse:
    """Создать задачу.

    Args:
        task: данные задачи (title обязателен).
        db: сессия БД (DI).

    Returns:
        Созданная задача со статусом 201.
    """
    return crud.create_task(db, task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)
) -> TaskResponse:
    """Частично обновить задачу по id.

    Raises:
        HTTPException: 404, если задача не найдена.
    """
    updated_task = crud.update_task(db, task_id, task_update)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)) -> None:
    """Удалить задачу по id.

    Raises:
        HTTPException: 404, если задача не найдена.
    """
    deleted = crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db)) -> TaskResponse:
    """Отметить задачу выполненной (is_done=True, фиксируется completed_at).

    Raises:
        HTTPException: 404, если задача не найдена.
    """
    updated_task = crud.update_task(db, task_id, TaskUpdate(is_done=True))
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Task not found"
        )
    return updated_task
