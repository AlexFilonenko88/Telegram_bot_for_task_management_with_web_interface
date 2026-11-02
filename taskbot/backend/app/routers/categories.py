"""Роутер категорий: /api/categories."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.deps import Pagination, paginate
from app.schemas.pagination import Page
from app.schemas.task import CategoryCreate, CategoryResponse

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.get("", response_model=Page[CategoryResponse])
def get_categories(
    user_id: int,
    pagination: Pagination = Depends(paginate),
    db: Session = Depends(get_db),
) -> Page[CategoryResponse]:
    """Постраничный список категорий пользователя."""
    categories = crud.get_categories_by_user(
        db, user_id, limit=pagination.limit, offset=pagination.offset
    )
    total = crud.count_categories_by_user(db, user_id)
    return Page(
        items=categories, total=total, limit=pagination.limit, offset=pagination.offset
    )


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category: CategoryCreate, db: Session = Depends(get_db)
) -> CategoryResponse:
    """Создать категорию (имя + владелец)."""
    return crud.create_category(db, category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    """Удалить категорию по id.

    Raises:
        HTTPException: 404, если категория не найдена.
    """
    deleted = crud.delete_category(db, category_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Category not found"
        )
