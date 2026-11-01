from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.task import TaskCreate, TaskUpdate, TaskResponse, CategoryCreate, CategoryResponse, TagCreate, TagResponse
from app import crud


router = APIRouter(prefix="/api/tasks", tags=["tasks"])
categories_router = APIRouter(prefix="/api/categories", tags=["categories"])
tags_router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=List[TaskResponse])
def get_tasks(user_id: int, db: Session = Depends(get_db)):
    tasks = crud.get_tasks_by_user(db, user_id=user_id)
    return tasks


@router.get("/stats/weekly")
def get_weekly_stats(user_id: int, db: Session = Depends(get_db)):
    """Get weekly task completion statistics."""
    return crud.get_weekly_stats(db, user_id)


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    return crud.create_task(db, task)


@router.put("/{task_id}", response_model=TaskResponse)
def update_task(task_id: int, task_update: TaskUpdate, db: Session = Depends(get_db)):
    updated_task = crud.update_task(db, task_id, task_update)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return updated_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )


@router.patch("/{task_id}/complete", response_model=TaskResponse)
def complete_task(task_id: int, db: Session = Depends(get_db)):
    task_update = TaskUpdate(is_done=True)
    updated_task = crud.update_task(db, task_id, task_update)
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    return updated_task


# Category endpoints
@categories_router.get("", response_model=List[CategoryResponse])
def get_categories(user_id: int, db: Session = Depends(get_db)):
    return crud.get_categories_by_user(db, user_id)


@categories_router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(category: CategoryCreate, db: Session = Depends(get_db)):
    return crud.create_category(db, category)


@categories_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )


# Tag endpoints
@tags_router.get("", response_model=List[TagResponse])
def get_tags(user_id: int, db: Session = Depends(get_db)):
    return crud.get_tags_by_user(db, user_id)


@tags_router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)):
    return crud.create_tag(db, tag)


@tags_router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_tag(db, tag_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tag not found"
        )
