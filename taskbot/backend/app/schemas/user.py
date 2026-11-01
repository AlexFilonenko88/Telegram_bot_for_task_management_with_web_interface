from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    telegram_id: int
    username: str
    first_name: str
    team_id: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: str
    first_name: str
    team_id: Optional[int] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TeamCreate(BaseModel):
    name: str

    model_config = ConfigDict(from_attributes=True)


class TeamResponse(BaseModel):
    id: int
    name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
