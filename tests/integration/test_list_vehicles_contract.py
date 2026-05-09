import os
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from domain.entities.vehicle import Vehicle

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")


def _make_vehicle(price: str) -> Vehicle:
    return Vehicle(
        brand="Toyota", model="Corolla", year=2023, color="Branco", price=Decimal(price)
    )


@pytest.fixture(scope="module")
def client():
    with patch("infrastructure.database.mongodb.init_db", new_callable=AsyncMock):
        from presentation.main import app

        with TestClient(app, raise_server_exceptions=False) as c:
            yield c


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token"}


@pytest.fixture(autouse=True)
def mock_auth():
    with patch("infrastructure.auth.oauth2.jwt.decode", return_value={"sub": "user1"}):
        yield


def test_get_vehicles_returns_200_with_empty_list(client, auth_headers):
    with patch(
        "application.use_cases.list_available_vehicles.ListAvailableVehicles.execute",
        new_callable=AsyncMock,
        return_value=([], 0),
    ):
        response = client.get("/vehicles", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["items"] == []
    assert body["total"] == 0
    assert body["page"] == 1
    assert body["page_size"] == 20


def test_get_vehicles_returns_items_ordered_by_price(client, auth_headers):
    v1 = _make_vehicle("30000")
    v2 = _make_vehicle("50000")
    with patch(
        "application.use_cases.list_available_vehicles.ListAvailableVehicles.execute",
        new_callable=AsyncMock,
        return_value=([v1, v2], 2),
    ):
        response = client.get("/vehicles", headers=auth_headers)

    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) == 2
    assert float(items[0]["price"]) < float(items[1]["price"])


def test_get_vehicles_respects_pagination_params(client, auth_headers):
    with patch(
        "application.use_cases.list_available_vehicles.ListAvailableVehicles.execute",
        new_callable=AsyncMock,
        return_value=([], 0),
    ) as mock_exec:
        response = client.get("/vehicles?page=2&page_size=5", headers=auth_headers)

    assert response.status_code == 200
    mock_exec.assert_called_once_with(page=2, page_size=5)
    body = response.json()
    assert body["page"] == 2
    assert body["page_size"] == 5


def test_get_vehicles_without_token_returns_401(client):
    response = client.get("/vehicles")
    assert response.status_code == 401


def test_get_vehicles_page_size_max_capped(client, auth_headers):
    with patch(
        "application.use_cases.list_available_vehicles.ListAvailableVehicles.execute",
        new_callable=AsyncMock,
        return_value=([], 0),
    ):
        response = client.get("/vehicles?page_size=200", headers=auth_headers)

    assert response.status_code == 422
