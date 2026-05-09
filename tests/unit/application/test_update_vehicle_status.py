from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from domain.entities.vehicle import Vehicle, VehicleStatus
from domain.repositories.vehicle_repository import VehicleRepository


def _make_vehicle(status: VehicleStatus = VehicleStatus.available) -> Vehicle:
    v = Vehicle(brand="Toyota", model="Corolla", year=2023, color="Branco", price=Decimal("85000"))
    if status == VehicleStatus.reserved:
        v.mark_as_reserved()
    elif status == VehicleStatus.sold:
        v.mark_as_reserved()
        v.mark_as_sold()
    return v


@pytest.mark.asyncio
async def test_update_status_available_to_reserved():
    from application.use_cases.update_vehicle_status import UpdateVehicleStatus

    vehicle = _make_vehicle(VehicleStatus.available)
    mock_repo = AsyncMock(spec=VehicleRepository)
    mock_repo.find_by_id.return_value = vehicle
    mock_repo.update_status.return_value = _make_vehicle(VehicleStatus.reserved)

    result = await UpdateVehicleStatus(mock_repo).execute(vehicle.id, VehicleStatus.reserved)

    assert result.status == VehicleStatus.reserved
    mock_repo.update_status.assert_called_once_with(vehicle.id, VehicleStatus.reserved)


@pytest.mark.asyncio
async def test_update_status_reserved_to_sold():
    from application.use_cases.update_vehicle_status import UpdateVehicleStatus

    vehicle = _make_vehicle(VehicleStatus.reserved)
    mock_repo = AsyncMock(spec=VehicleRepository)
    mock_repo.find_by_id.return_value = vehicle
    mock_repo.update_status.return_value = _make_vehicle(VehicleStatus.sold)

    result = await UpdateVehicleStatus(mock_repo).execute(vehicle.id, VehicleStatus.sold)

    assert result.status == VehicleStatus.sold


@pytest.mark.asyncio
async def test_update_status_reserved_to_available():
    from application.use_cases.update_vehicle_status import UpdateVehicleStatus

    vehicle = _make_vehicle(VehicleStatus.reserved)
    mock_repo = AsyncMock(spec=VehicleRepository)
    mock_repo.find_by_id.return_value = vehicle
    mock_repo.update_status.return_value = _make_vehicle(VehicleStatus.available)

    result = await UpdateVehicleStatus(mock_repo).execute(vehicle.id, VehicleStatus.available)

    assert result.status == VehicleStatus.available


@pytest.mark.asyncio
async def test_update_status_available_to_sold_raises_conflict():
    from application.use_cases.update_vehicle_status import ConflictError, UpdateVehicleStatus

    vehicle = _make_vehicle(VehicleStatus.available)
    mock_repo = AsyncMock(spec=VehicleRepository)
    mock_repo.find_by_id.return_value = vehicle

    with pytest.raises(ConflictError):
        await UpdateVehicleStatus(mock_repo).execute(vehicle.id, VehicleStatus.sold)


@pytest.mark.asyncio
async def test_update_status_sold_to_any_raises_conflict():
    from application.use_cases.update_vehicle_status import ConflictError, UpdateVehicleStatus

    vehicle = _make_vehicle(VehicleStatus.sold)
    mock_repo = AsyncMock(spec=VehicleRepository)
    mock_repo.find_by_id.return_value = vehicle

    for target in (VehicleStatus.available, VehicleStatus.reserved, VehicleStatus.sold):
        mock_repo.reset_mock()
        with pytest.raises(ConflictError):
            await UpdateVehicleStatus(mock_repo).execute(vehicle.id, target)


@pytest.mark.asyncio
async def test_update_status_not_found_raises():
    from application.use_cases.update_vehicle_status import NotFoundError, UpdateVehicleStatus

    mock_repo = AsyncMock(spec=VehicleRepository)
    mock_repo.find_by_id.return_value = None

    with pytest.raises(NotFoundError):
        await UpdateVehicleStatus(mock_repo).execute(uuid4(), VehicleStatus.reserved)
