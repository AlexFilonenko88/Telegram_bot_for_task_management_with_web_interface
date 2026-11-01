from datetime import datetime
from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    telegram_id: int
    username: str
    first_name: str

    model_config = ConfigDict(from_attributes=True)


class UserResponse(BaseModel):
    id: int
    telegram_id: int
    username: str
    first_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
