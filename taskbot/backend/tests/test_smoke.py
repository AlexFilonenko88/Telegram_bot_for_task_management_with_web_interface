# =============================================================================
# Смоук-тесты для CI (GitHub Actions, п.16): проверяют, что приложение
# импортируется, стартует и отдаёт основные эндпоинты.
# Полные тесты API добавляются по мере развития проекта в этой же папке.
# =============================================================================

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_openapi_schema_reachable():
    """Swagger-схема отдаётся без ошибок (быстрый признак битого импорта схем)."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()


def test_tasks_routes_registered():
    """Маршруты задач /api/tasks зарегистрированы и видны в API.

    В FastAPI 0.162 включённые роутеры лежат в app.routes как вложенные
    _IncludedRouter (без атрибута path), поэтому реальные пути проверяем
    по OpenAPI-схеме — это фактическая поверхность API, которую видит
    и Swagger, и клиенты.
    """
    response = client.get("/openapi.json")
    assert response.status_code == 200
    paths = response.json()["paths"]
    assert any(path.startswith("/api/tasks") for path in paths), (
        f"Маршруты /api/tasks не зарегистрированы; доступные пути: {sorted(paths)}"
    )
