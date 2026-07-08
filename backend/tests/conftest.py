from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.db.session import engine
from app.main import app


@pytest.fixture
def client() -> Generator[TestClient, None, None]:
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def _clean_transactions() -> Generator[None, None, None]:
    """Limpia la tabla `transactions` antes y después de cada test para aislarlos entre sí."""
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM transactions"))
    yield
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM transactions"))