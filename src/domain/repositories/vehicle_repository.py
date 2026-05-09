from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.vehicle import Vehicle, VehicleStatus


class VehicleRepository(ABC):
    @abstractmethod
    async def save(self, vehicle: Vehicle) -> Vehicle: ...

    @abstractmethod
    async def find_by_id(self, vehicle_id: UUID) -> Vehicle | None: ...

    @abstractmethod
    async def update(self, vehicle: Vehicle) -> Vehicle: ...

    @abstractmethod
    async def update_status(self, vehicle_id: UUID, status: VehicleStatus) -> Vehicle | None: ...

    @abstractmethod
    async def list_available(self, page: int, page_size: int) -> tuple[list[Vehicle], int]: ...
