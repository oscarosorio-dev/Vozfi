from fastapi.testclient import TestClient


def _create_transaction(client: TestClient, **overrides) -> dict:
    payload = {
        "type": "expense",
        "amount": 20000,
        "category": "comida",
        "description": "almuerzo",
        "occurred_at": "2026-07-04T12:00:00Z",
        **overrides,
    }
    response = client.post("/transactions", json=payload)
    assert response.status_code == 201
    return response.json()


def test_create_transaction(client: TestClient) -> None:
    data = _create_transaction(client)
    assert data["type"] == "expense"
    assert data["amount"] == 20000
    assert data["category"] == "comida"
    assert "id" in data


def test_list_transactions(client: TestClient) -> None:
    _create_transaction(client, category="comida")
    _create_transaction(client, category="transporte", type="income", amount=5000)

    response = client.get("/transactions")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_transaction(client: TestClient) -> None:
    created = _create_transaction(client)

    response = client.get(f"/transactions/{created['id']}")
    assert response.status_code == 200
    assert response.json()["id"] == created["id"]


def test_get_transaction_not_found(client: TestClient) -> None:
    response = client.get("/transactions/00000000-0000-0000-0000-000000000000")
    assert response.status_code == 404


def test_delete_transaction(client: TestClient) -> None:
    created = _create_transaction(client)

    response = client.delete(f"/transactions/{created['id']}")
    assert response.status_code == 204

    response = client.get(f"/transactions/{created['id']}")
    assert response.status_code == 404


def test_create_transaction_invalid_amount(client: TestClient) -> None:
    response = client.post(
        "/transactions",
        json={
            "type": "expense",
            "amount": -10,
            "category": "comida",
            "occurred_at": "2026-07-04T12:00:00Z",
        },
    )
    assert response.status_code == 422