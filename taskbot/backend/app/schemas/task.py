from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    name: str
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class CategoryResponse(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TagCreate(BaseModel):
    name: str
    user_id: int

    model_config = ConfigDict(from_attributes=True)


class TagResponse(BaseModel):
    id: int
    name: str
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    user_id: int
    priority: Optional[str] = None  # low, medium, high
    deadline: Optional[datetime] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None

    model_config = ConfigDict(from_attributes=True)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_done: Optional[bool] = None
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    category_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None

    model_config = ConfigDict(from_attributes=True)


class TaskResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    is_done: bool
    priority: Optional[str] = None
    deadline: Optional[datetime] = None
    category_id: Optional[int] = None
    category: Optional[CategoryResponse] = None
    tags: List[TagResponse] = []
    reminder_sent: bool
    created_at: datetime
    completed_at: Optional[datetime] = None
    user_id: int

    model_config = ConfigDict(from_attributes=True)
