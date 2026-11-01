from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.user import UserCreate, UserResponse, TeamCreate, TeamResponse
from app import crud


router = APIRouter(prefix="/api/users", tags=["users"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_telegram_id(db, user.telegram_id)
    if db_user:
        return db_user
    return crud.create_user(db, user)


@router.post("/join-team/{user_id}/{team_id}", response_model=UserResponse)
def join_team(user_id: int, team_id: int, db: Session = Depends(get_db)):
    user = crud.add_user_to_team(db, user_id, team_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
