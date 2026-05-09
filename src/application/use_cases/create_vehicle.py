from decimal import Decimal

from domain.entities.vehicle import Vehicle
from domain.repositories.vehicle_repository import VehicleRepository


class CreateVehicle:
    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        brand: str,
        model: str,
        year: int,
        color: str,
        price: Decimal,
    ) -> Vehicle:
        vehicle = Vehicle(
            brand=brand,
            model=model,
            year=year,
            color=color,
            price=price,
        )
        return await self._repository.save(vehicle)
