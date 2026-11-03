# =============================================================================
# Смоук-тесты для CI (GitHub Actions, п.16): проверяют, что приложение
# импортируется, собирается и отвечает на базовые запросы.
# Полные тесты API добавляются по мере развития проекта в этой же папке.
# =============================================================================

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_app_imports_and_has_routes():
    """Приложение создаётся и содержит основные маршруты."""
    routes = {r.path for r in app.routes}
    assert "/openapi.json" in routes
    assert any(path.startswith("/api/tasks") for path in routes), (
        "Маршруты задач /api/tasks не зарегистрированы"
    )


def test_openapi_schema_reachable():
    """Swagger-схема отдаётся без ошибок (быстрый признак битого импорта схем)."""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()
