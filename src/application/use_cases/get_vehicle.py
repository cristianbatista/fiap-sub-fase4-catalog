from uuid import UUID

from domain.entities.vehicle import Vehicle
from domain.repositories.vehicle_repository import VehicleRepository


class NotFoundError(Exception):
    pass


class GetVehicle:
    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    async def execute(self, vehicle_id: UUID) -> Vehicle:
        vehicle = await self._repository.find_by_id(vehicle_id)
        if vehicle is None:
            raise NotFoundError(f"Veículo {vehicle_id} não encontrado")
        return vehicle
