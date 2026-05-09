import os
from decimal import Decimal
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from domain.entities.vehicle import Vehicle, VehicleStatus

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
        status=VehicleStatus.available,
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


_valid_payload = {
    "brand": "Honda",
    "model": "Civic",
    "year": 2022,
    "color": "Preto",
    "price": "90000.00",
}


def test_put_vehicle_returns_200(client, auth_headers):
    vehicle = _make_vehicle()
    updated = Vehicle(**{**vehicle.model_dump(), "brand": "Honda", "model": "Civic"})
    with patch(
        "application.use_cases.update_vehicle.UpdateVehicle.execute",
        new_callable=AsyncMock,
        return_value=updated,
    ):
        response = client.put(f"/vehicles/{vehicle.id}", json=_valid_payload, headers=auth_headers)

    assert response.status_code == 200
    body = response.json()
    assert body["brand"] == "Honda"
    assert "updated_at" in body


def test_put_vehicle_not_found_returns_404(client, auth_headers):
    from application.use_cases.update_vehicle import NotFoundError

    with patch(
        "application.use_cases.update_vehicle.UpdateVehicle.execute",
        new_callable=AsyncMock,
        side_effect=NotFoundError("not found"),
    ):
        response = client.put(f"/vehicles/{uuid4()}", json=_valid_payload, headers=auth_headers)

    assert response.status_code == 404
    assert "não encontrado" in response.json()["detail"].lower()


def test_put_vehicle_without_token_returns_401(client):
    response = client.put(f"/vehicles/{uuid4()}", json=_valid_payload)
    assert response.status_code == 401


def test_put_vehicle_negative_price_returns_422(client, auth_headers):
    payload = {**_valid_payload, "price": "-1"}
    response = client.put(f"/vehicles/{uuid4()}", json=payload, headers=auth_headers)
    assert response.status_code == 422
