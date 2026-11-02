"""Общие зависимости FastAPI (dependency injection)."""

from dataclasses import dataclass

from fastapi import Query


@dataclass(frozen=True)
class Pagination:
    """Вычисленные параметры пагинации для спискового эндпоинта."""

    limit: int
    offset: int


def paginate(
    limit: int = Query(50, ge=1, le=100, description="Размер страницы (1–100)"),
    offset: int = Query(0, ge=0, description="Смещение первой записи"),
) -> Pagination:
    """Зависимость пагинации: валидирует query-параметры limit/offset.

    Ограничение le=100 защищает API от запросов «выдай всё»
    (limit=1000000), способных положить и БД, и сериализацию ответа.
    """
    return Pagination(limit=limit, offset=offset)
