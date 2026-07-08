from fastapi.testclient import TestClient


def _seed(client: TestClient) -> None:
    client.post(
        "/transactions",
        json={
            "type": "income",
            "amount": 1000,
            "category": "salario",
            "occurred_at": "2026-07-01T09:00:00Z",
        },
    )
    client.post(
        "/transactions",
        json={
            "type": "expense",
            "amount": 200,
            "category": "comida",
            "occurred_at": "2026-07-02T09:00:00Z",
        },
    )


def test_balance(client: TestClient) -> None:
    _seed(client)

    response = client.get("/summary/balance")
    assert response.status_code == 200
    data = response.json()
    assert data["income"] == 1000
    assert data["expense"] == 200
    assert data["balance"] == 800


def test_balance_sin_transacciones(client: TestClient) -> None:
    response = client.get("/summary/balance")
    assert response.status_code == 200
    assert response.json() == {"income": 0, "expense": 0, "balance": 0}


def test_summary_by_month(client: TestClient) -> None:
    client.post(
        "/transactions",
        json={"type": "income", "amount": 1000, "category": "salario", "occurred_at": "2026-05-15T09:00:00Z"},
    )
    client.post(
        "/transactions",
        json={"type": "expense", "amount": 200, "category": "comida", "occurred_at": "2026-05-20T09:00:00Z"},
    )
    client.post(
        "/transactions",
        json={"type": "income", "amount": 2000, "category": "salario", "occurred_at": "2026-06-15T09:00:00Z"},
    )

    response = client.get("/summary/by-month")
    assert response.status_code == 200
    data = response.json()
    assert data == [
        {"month": "2026-05", "income": 1000, "expense": 200, "balance": 800},
        {"month": "2026-06", "income": 2000, "expense": 0, "balance": 2000},
    ]


def test_summary_by_month_vacio(client: TestClient) -> None:
    response = client.get("/summary/by-month")
    assert response.status_code == 200
    assert response.json() == []
    _seed(client)

    response = client.get("/summary/by-category")
    assert response.status_code == 200
    categories = {item["category"] for item in response.json()}
    assert categories == {"salario", "comida"}