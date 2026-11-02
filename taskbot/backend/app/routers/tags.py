"""Роутер тегов: /api/tags."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.deps import Pagination, paginate
from app.schemas.pagination import Page
from app.schemas.task import TagCreate, TagResponse

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("", response_model=Page[TagResponse])
def get_tags(
    user_id: int,
    pagination: Pagination = Depends(paginate),
    db: Session = Depends(get_db),
) -> Page[TagResponse]:
    """Постраничный список тегов пользователя."""
    tags = crud.get_tags_by_user(
        db, user_id, limit=pagination.limit, offset=pagination.offset
    )
    total = crud.count_tags_by_user(db, user_id)
    return Page(
        items=tags, total=total, limit=pagination.limit, offset=pagination.offset
    )


@router.post("", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
def create_tag(tag: TagCreate, db: Session = Depends(get_db)) -> TagResponse:
    """Создать тег (имя + владелец)."""
    return crud.create_tag(db, tag)


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_tag(tag_id: int, db: Session = Depends(get_db)) -> None:
    """Удалить тег по id.

    Raises:
        HTTPException: 404, если тег не найден.
    """
    deleted = crud.delete_tag(db, tag_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found"
        )
