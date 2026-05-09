from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from domain.entities.vehicle import Vehicle, VehicleStatus
from domain.repositories.vehicle_repository import VehicleRepository


class FakeVehicleRepository(VehicleRepository):
    def __init__(self):
        self._store: dict = {}

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
async def test_create_vehicle_returns_vehicle_with_id():
    from application.use_cases.create_vehicle import CreateVehicle

    repo = FakeVehicleRepository()
    use_case = CreateVehicle(repo)

    vehicle = await use_case.execute(
        brand="Toyota",
        model="Corolla",
        year=2023,
        color="Branco",
        price=Decimal("85000.00"),
    )

    assert vehicle.id is not None
    assert vehicle.brand == "Toyota"
    assert vehicle.model == "Corolla"
    assert vehicle.year == 2023
    assert vehicle.color == "Branco"
    assert vehicle.price == Decimal("85000.00")
    assert vehicle.status == VehicleStatus.available


@pytest.mark.asyncio
async def test_create_vehicle_persists_to_repository():
    from application.use_cases.create_vehicle import CreateVehicle

    repo = FakeVehicleRepository()
    use_case = CreateVehicle(repo)

    vehicle = await use_case.execute(
        brand="Honda",
        model="Civic",
        year=2022,
        color="Preto",
        price=Decimal("90000.00"),
    )

    stored = await repo.find_by_id(vehicle.id)
    assert stored is not None
    assert stored.brand == "Honda"


@pytest.mark.asyncio
async def test_create_vehicle_calls_repository_save():
    from application.use_cases.create_vehicle import CreateVehicle

    mock_repo = AsyncMock(spec=VehicleRepository)
    mock_repo.save.return_value = Vehicle(
        brand="Ford",
        model="Ka",
        year=2021,
        color="Vermelho",
        price=Decimal("45000.00"),
    )

    use_case = CreateVehicle(mock_repo)
    await use_case.execute(
        brand="Ford",
        model="Ka",
        year=2021,
        color="Vermelho",
        price=Decimal("45000.00"),
    )

    mock_repo.save.assert_called_once()
