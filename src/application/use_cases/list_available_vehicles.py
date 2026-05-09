from domain.entities.vehicle import Vehicle
from domain.repositories.vehicle_repository import VehicleRepository


class ListAvailableVehicles:
    def __init__(self, repository: VehicleRepository) -> None:
        self._repository = repository

    async def execute(self, page: int, page_size: int) -> tuple[list[Vehicle], int]:
        return await self._repository.list_available(page=page, page_size=page_size)
