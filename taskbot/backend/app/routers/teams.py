from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import TeamCreate, TeamResponse
from app.schemas.task import TaskResponse
from app import crud


router = APIRouter(prefix="/api/teams", tags=["teams"])


@router.post("", response_model=TeamResponse, status_code=status.HTTP_201_CREATED)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    existing_team = crud.get_team_by_name(db, team.name)
    if existing_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Team with this name already exists"
        )
    return crud.create_team(db, team)


@router.get("/{team_id}/tasks", response_model=List[TaskResponse])
def get_team_tasks(team_id: int, db: Session = Depends(get_db)):
    return crud.get_team_tasks(db, team_id)


@router.get("/{team_id}/stats/weekly")
def get_team_weekly_stats(team_id: int, db: Session = Depends(get_db)):
    """Get team weekly task completion statistics."""
    return crud.get_team_weekly_stats(db, team_id)
