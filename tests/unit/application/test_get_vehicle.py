from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from domain.entities.vehicle import Vehicle
from domain.repositories.vehicle_repository import VehicleRepository


def _make_vehicle() -> Vehicle:
    return Vehicle(brand="Toyota", model="Corolla", year=2023, color="Branco", price=Decimal("85000"))


@pytest.mark.asyncio
async def test_get_vehicle_returns_vehicle():
    from application.use_cases.get_vehicle import GetVehicle

    vehicle = _make_vehicle()
    mock_repo = AsyncMock(spec=VehicleRepository)
    mock_repo.find_by_id.return_value = vehicle

    use_case = GetVehicle(mock_repo)
    result = await use_case.execute(vehicle.id)

    assert result.id == vehicle.id
    assert result.brand == "Toyota"
    mock_repo.find_by_id.assert_called_once_with(vehicle.id)


@pytest.mark.asyncio
async def test_get_vehicle_not_found_raises():
    from application.use_cases.get_vehicle import GetVehicle, NotFoundError

    mock_repo = AsyncMock(spec=VehicleRepository)
    mock_repo.find_by_id.return_value = None

    use_case = GetVehicle(mock_repo)
    with pytest.raises(NotFoundError):
        await use_case.execute(uuid4())
