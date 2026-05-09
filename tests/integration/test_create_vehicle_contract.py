import os
from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient

from domain.entities.vehicle import Vehicle, VehicleStatus

os.environ.setdefault("MONGODB_URI", "mongodb://localhost:27017/test")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")


def _mock_vehicle() -> Vehicle:
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


def test_post_vehicles_returns_201(client, auth_headers):
    vehicle = _mock_vehicle()
    with patch(
        "application.use_cases.create_vehicle.CreateVehicle.execute",
        new_callable=AsyncMock,
        return_value=vehicle,
    ):
        response = client.post(
            "/vehicles",
            json={
                "brand": "Toyota",
                "model": "Corolla",
                "year": 2023,
                "color": "Branco",
                "price": "85000.00",
            },
            headers=auth_headers,
        )

    assert response.status_code == 201
    body = response.json()
    assert body["brand"] == "Toyota"
    assert body["status"] == "available"
    assert "id" in body
    assert "created_at" in body


def test_post_vehicles_without_token_returns_401(client):
    response = client.post(
        "/vehicles",
        json={"brand": "Toyota", "model": "Corolla", "year": 2023, "color": "Branco", "price": "85000.00"},
    )
    assert response.status_code == 401


def test_post_vehicles_missing_field_returns_422(client, auth_headers):
    response = client.post(
        "/vehicles",
        json={"brand": "Toyota", "model": "Corolla", "year": 2023, "color": "Branco"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_post_vehicles_negative_price_returns_422(client, auth_headers):
    response = client.post(
        "/vehicles",
        json={"brand": "Toyota", "model": "Corolla", "year": 2023, "color": "Branco", "price": "-1"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_post_vehicles_invalid_year_returns_422(client, auth_headers):
    response = client.post(
        "/vehicles",
        json={"brand": "Toyota", "model": "Corolla", "year": 1800, "color": "Branco", "price": "50000"},
        headers=auth_headers,
    )
    assert response.status_code == 422
