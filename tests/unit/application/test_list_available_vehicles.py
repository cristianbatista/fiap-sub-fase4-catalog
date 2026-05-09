from decimal import Decimal

import pytest

from domain.entities.vehicle import Vehicle, VehicleStatus
from domain.repositories.vehicle_repository import VehicleRepository


def _make_vehicle(
    price: Decimal, status: VehicleStatus = VehicleStatus.available
) -> Vehicle:
    v = Vehicle(brand="X", model="Y", year=2022, color="Z", price=price)
    if status == VehicleStatus.sold:
        v.mark_as_sold()
    return v


class FakeVehicleRepository(VehicleRepository):
    def __init__(self, vehicles: list[Vehicle] | None = None):
        self._store = {v.id: v for v in (vehicles or [])}

    async def save(self, vehicle):
        self._store[vehicle.id] = vehicle
        return vehicle

    async def find_by_id(self, vehicle_id):
        return self._store.get(vehicle_id)

    async def update(self, vehicle):
        self._store[vehicle.id] = vehicle
        return vehicle

    async def update_status(self, vehicle_id, status):
        v = self._store.get(vehicle_id)
        if v:
            v.status = status
        return v

    async def list_available(
        self, page: int, page_size: int
    ) -> tuple[list[Vehicle], int]:
        items = sorted(
            [v for v in self._store.values() if v.status == VehicleStatus.available],
            key=lambda v: v.price,
        )
        total = len(items)
        skip = (page - 1) * page_size
        return items[skip : skip + page_size], total


@pytest.mark.asyncio
async def test_list_returns_only_available():
    from application.use_cases.list_available_vehicles import ListAvailableVehicles

    available = _make_vehicle(Decimal("50000"))
    sold = _make_vehicle(Decimal("30000"), VehicleStatus.sold)
    repo = FakeVehicleRepository([available, sold])
    use_case = ListAvailableVehicles(repo)

    items, total = await use_case.execute(page=1, page_size=20)

    assert total == 1
    assert len(items) == 1
    assert items[0].id == available.id


@pytest.mark.asyncio
async def test_list_empty_when_no_vehicles():
    from application.use_cases.list_available_vehicles import ListAvailableVehicles

    repo = FakeVehicleRepository()
    use_case = ListAvailableVehicles(repo)

    items, total = await use_case.execute(page=1, page_size=20)

    assert items == []
    assert total == 0


@pytest.mark.asyncio
async def test_list_ordered_by_price_ascending():
    from application.use_cases.list_available_vehicles import ListAvailableVehicles

    v1 = _make_vehicle(Decimal("90000"))
    v2 = _make_vehicle(Decimal("30000"))
    v3 = _make_vehicle(Decimal("60000"))
    repo = FakeVehicleRepository([v1, v2, v3])
    use_case = ListAvailableVehicles(repo)

    items, _ = await use_case.execute(page=1, page_size=20)

    assert items[0].price == Decimal("30000")
    assert items[1].price == Decimal("60000")
    assert items[2].price == Decimal("90000")


@pytest.mark.asyncio
async def test_list_pagination_page_2():
    from application.use_cases.list_available_vehicles import ListAvailableVehicles

    vehicles = [_make_vehicle(Decimal(str(i * 10000))) for i in range(1, 6)]
    repo = FakeVehicleRepository(vehicles)
    use_case = ListAvailableVehicles(repo)

    items, total = await use_case.execute(page=2, page_size=2)

    assert total == 5
    assert len(items) == 2
    assert items[0].price == Decimal("30000")


@pytest.mark.asyncio
async def test_list_pagination_last_page_partial():
    from application.use_cases.list_available_vehicles import ListAvailableVehicles

    vehicles = [_make_vehicle(Decimal(str(i * 10000))) for i in range(1, 6)]
    repo = FakeVehicleRepository(vehicles)
    use_case = ListAvailableVehicles(repo)

    items, total = await use_case.execute(page=3, page_size=2)

    assert total == 5
    assert len(items) == 1
