from decimal import Decimal
from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from domain.entities.vehicle import Vehicle, VehicleStatus
from domain.repositories.vehicle_repository import VehicleRepository


def _make_vehicle(**kwargs) -> Vehicle:
    defaults = dict(
        brand="Toyota",
        model="Corolla",
        year=2023,
        color="Branco",
        price=Decimal("85000"),
    )
    return Vehicle(**{**defaults, **kwargs})


class FakeVehicleRepository(VehicleRepository):
    def __init__(self, initial: Vehicle | None = None):
        self._store: dict = {}
        if initial:
            self._store[initial.id] = initial

    async def save(self, vehicle: Vehicle) -> Vehicle:
        self._store[vehicle.id] = vehicle
        return vehicle

    async def find_by_id(self, vehicle_id):
        return self._store.get(vehicle_id)

    async def update(self, vehicle: Vehicle) -> Vehicle:
        self._store[vehicle.id] = vehicle
        return vehicle

    async def update_status(self, vehicle_id, status):
        v = self._store.get(vehicle_id)
        if v:
            v.status = status
        return v

    async def list_available(self, page, page_size):
        items = [v for v in self._store.values() if v.status == VehicleStatus.available]
        return items, len(items)


@pytest.mark.asyncio
async def test_update_vehicle_success():
    from application.use_cases.update_vehicle import UpdateVehicle

    vehicle = _make_vehicle()
    repo = FakeVehicleRepository(initial=vehicle)
    use_case = UpdateVehicle(repo)

    updated = await use_case.execute(
        vehicle_id=vehicle.id,
        brand="Honda",
        model="Civic",
        year=2022,
        color="Preto",
        price=Decimal("90000"),
    )

    assert updated.brand == "Honda"
    assert updated.model == "Civic"
    assert updated.price == Decimal("90000")


@pytest.mark.asyncio
async def test_update_vehicle_not_found_raises():
    from application.use_cases.update_vehicle import NotFoundError, UpdateVehicle

    repo = FakeVehicleRepository()
    use_case = UpdateVehicle(repo)

    with pytest.raises(NotFoundError):
        await use_case.execute(
            vehicle_id=uuid4(),
            brand="Honda",
            model="Civic",
            year=2022,
            color="Preto",
            price=Decimal("90000"),
        )


@pytest.mark.asyncio
async def test_update_vehicle_calls_repository_update():
    from application.use_cases.update_vehicle import UpdateVehicle

    vehicle = _make_vehicle()
    mock_repo = AsyncMock(spec=VehicleRepository)
    mock_repo.find_by_id.return_value = vehicle
    mock_repo.update.return_value = vehicle

    use_case = UpdateVehicle(mock_repo)
    await use_case.execute(
        vehicle_id=vehicle.id,
        brand="Ford",
        model="Ka",
        year=2021,
        color="Vermelho",
        price=Decimal("45000"),
    )

    mock_repo.update.assert_called_once()


@pytest.mark.asyncio
async def test_update_vehicle_preserves_status():
    from application.use_cases.update_vehicle import UpdateVehicle

    vehicle = _make_vehicle()
    vehicle.mark_as_reserved()
    vehicle.mark_as_sold()
    repo = FakeVehicleRepository(initial=vehicle)
    use_case = UpdateVehicle(repo)

    updated = await use_case.execute(
        vehicle_id=vehicle.id,
        brand="Honda",
        model="Civic",
        year=2022,
        color="Preto",
        price=Decimal("90000"),
    )

    assert updated.status == VehicleStatus.sold
