"""Роутер команд: /api/teams."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud
from app.database import get_db
from app.deps import Pagination, paginate
from app.schemas.pagination import Page
from app.schemas.task import TaskResponse
from app.schemas.user import TeamCreate, TeamResponse

router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(team: TeamCreate, db: Session = Depends(get_db)) -> TeamResponse:
    """Создать команду с уникальным именем.

    Raises:
        HTTPException: 400, если команда с таким именем уже существует.
    """
    existing_team = crud.get_team_by_name(db, team.name)
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team with this name already exists",
        )
    return crud.create_team(db, team)


@router.get("/{team_id}/tasks", response_model=Page[TaskResponse])
def get_team_tasks(
    team_id: int,
    pagination: Pagination = Depends(paginate),
    db: Session = Depends(get_db),
) -> Page[TaskResponse]:
    """Постраничный список задач всех участников команды."""
    tasks = crud.get_team_tasks(
        db, team_id, limit=pagination.limit, offset=pagination.offset
    )
    total = crud.count_team_tasks(db, team_id)
    return Page(
        items=tasks, total=total, limit=pagination.limit, offset=pagination.offset
    )


@router.get("/{team_id}/stats/weekly")
def get_team_weekly_stats(team_id: int, db: Session = Depends(get_db)) -> dict:
    """Статистика выполнения задач команды за последние 7 дней."""
    return crud.get_team_weekly_stats(db, team_id)
