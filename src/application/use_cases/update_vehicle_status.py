from uuid import UUID

from domain.entities.vehicle import Vehicle, VehicleStatus
from domain.repositories.vehicle_repository import VehicleRepository


class NotFoundError(Exception):
    pass


class ConflictError(Exception):
    pass


class UpdateVehicleStatus:
    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    async def execute(self, vehicle_id: UUID, status: VehicleStatus) -> Vehicle:
        vehicle = await self._repository.find_by_id(vehicle_id)
        if vehicle is None:
            raise NotFoundError(f"Veículo {vehicle_id} não encontrado")

        if vehicle.status == status:
            raise ConflictError(
                f"Veículo já está com status '{status.value}'. Transição inválida."
            )

        updated = await self._repository.update_status(vehicle_id, status)
        return updated
