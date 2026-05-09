from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID

from domain.entities.vehicle import Vehicle
from domain.repositories.vehicle_repository import VehicleRepository


class NotFoundError(Exception):
    pass


class UpdateVehicle:
    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    async def execute(
        self,
        vehicle_id: UUID,
        brand: str,
        model: str,
        year: int,
        color: str,
        price: Decimal,
    ) -> Vehicle:
        vehicle = await self._repository.find_by_id(vehicle_id)
        if vehicle is None:
            raise NotFoundError(f"Veículo {vehicle_id} não encontrado")

        vehicle.brand = brand
        vehicle.model = model
        vehicle.year = year
        vehicle.color = color
        vehicle.price = round(price, 2)
        vehicle.updated_at = datetime.now(timezone.utc)

        return await self._repository.update(vehicle)
