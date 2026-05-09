import os
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from domain.entities.vehicle import Vehicle

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")


def _make_vehicle() -> Vehicle:
    return Vehicle(
        brand="Toyota",
        model="Corolla",
        year=2023,
        color="Branco",
        price=Decimal("85000.00"),
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


def test_get_vehicle_by_id_returns_200(client, auth_headers):
    vehicle = _make_vehicle()
    with patch(
        "application.use_cases.get_vehicle.GetVehicle.execute",
        new_callable=AsyncMock,
        return_value=vehicle,
    ):
        response = client.get(f"/vehicles/{vehicle.id}", headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["id"] == str(vehicle.id)
    assert body["brand"] == "Toyota"
    assert "created_at" in body


def test_get_vehicle_not_found_returns_404(client, auth_headers):
    from application.use_cases.get_vehicle import NotFoundError

    with patch(
        "application.use_cases.get_vehicle.GetVehicle.execute",
        new_callable=AsyncMock,
        side_effect=NotFoundError("not found"),
    ):
        response = client.get(f"/vehicles/{uuid4()}", headers=auth_headers)

    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"].lower()


def test_get_vehicle_without_token_returns_401(client):
    response = client.get(f"/vehicles/{uuid4()}")
    assert response.status_code == 401
