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


def _make_vehicle(status: VehicleStatus = VehicleStatus.available) -> Vehicle:
    v = Vehicle(brand="Toyota", model="Corolla", year=2023, color="Branco", price=Decimal("85000.00"))
    if status == VehicleStatus.reserved:
        v.mark_as_reserved()
    elif status == VehicleStatus.sold:
        v.mark_as_reserved()
        v.mark_as_sold()
    return v


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


def test_patch_status_available_to_reserved_returns_200(client, auth_headers):
    vehicle = _make_vehicle(VehicleStatus.reserved)
    with patch(
        "application.use_cases.update_vehicle_status.UpdateVehicleStatus.execute",
        new_callable=AsyncMock,
        return_value=vehicle,
    ):
        response = client.patch(
            f"/vehicles/{uuid4()}/status",
            json={"status": "reserved"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    assert response.json()["status"] == "reserved"


def test_patch_status_reserved_to_sold_returns_200(client, auth_headers):
    vehicle = _make_vehicle(VehicleStatus.sold)
    with patch(
        "application.use_cases.update_vehicle_status.UpdateVehicleStatus.execute",
        new_callable=AsyncMock,
        return_value=vehicle,
    ):
        response = client.patch(
            f"/vehicles/{uuid4()}/status",
            json={"status": "sold"},
            headers=auth_headers,
        )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "sold"
    assert "updated_at" in body


def test_patch_status_conflict_returns_409(client, auth_headers):
    from application.use_cases.update_vehicle_status import ConflictError

    with patch(
        "application.use_cases.update_vehicle_status.UpdateVehicleStatus.execute",
        new_callable=AsyncMock,
        side_effect=ConflictError("already sold"),
    ):
        response = client.patch(
            f"/vehicles/{uuid4()}/status",
            json={"status": "sold"},
            headers=auth_headers,
        )

    assert response.status_code == 409
    assert "conflito" in response.json()["detail"].lower()


def test_patch_status_not_found_returns_404(client, auth_headers):
    from application.use_cases.update_vehicle_status import NotFoundError

    with patch(
        "application.use_cases.update_vehicle_status.UpdateVehicleStatus.execute",
        new_callable=AsyncMock,
        side_effect=NotFoundError("not found"),
    ):
        response = client.patch(
            f"/vehicles/{uuid4()}/status",
            json={"status": "sold"},
            headers=auth_headers,
        )

    assert response.status_code == 404


def test_patch_status_invalid_value_returns_422(client, auth_headers):
    response = client.patch(
        f"/vehicles/{uuid4()}/status",
        json={"status": "invalid"},
        headers=auth_headers,
    )
    assert response.status_code == 422


def test_patch_status_without_token_returns_401(client):
    response = client.patch(f"/vehicles/{uuid4()}/status", json={"status": "sold"})
    assert response.status_code == 401
