from collections.abc import Generator

import pytest
from sqlalchemy import text

from src.database import engine


@pytest.fixture(autouse=True)
def _clean_transactions() -> Generator[None, None, None]:
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM transactions"))
    yield
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM transactions"))