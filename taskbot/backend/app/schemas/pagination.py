"""Схема постраничного ответа API.

Все эндпоинты, возвращающие списки, оборачивают результат в Page[T]:
клиент получает страницу элементов и метаданные для навигации.
"""

from typing import Generic, List, TypeVar

from pydantic import BaseModel, Field

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    """Конверт постраничного ответа: элементы страницы + метаданные пагинации."""

    items: List[T] = Field(description="Элементы текущей страницы")
    total: int = Field(ge=0, description="Общее число элементов по фильтру (без пагинации)")
    limit: int = Field(ge=1, description="Размер страницы")
    offset: int = Field(ge=0, description="Смещение первого элемента страницы")
