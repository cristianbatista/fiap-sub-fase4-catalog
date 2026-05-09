from uuid import UUID

from domain.entities.vehicle import Vehicle, VehicleStatus
from domain.repositories.vehicle_repository import VehicleRepository

_TRANSITION_METHOD = {
    VehicleStatus.reserved: lambda v: v.mark_as_reserved(),
    VehicleStatus.sold: lambda v: v.mark_as_sold(),
    VehicleStatus.available: lambda v: v.mark_as_available(),
}


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

        try:
            _TRANSITION_METHOD[status](vehicle)
        except ValueError as err:
            raise ConflictError(str(err)) from err

        return await self._repository.update_status(vehicle_id, status)
