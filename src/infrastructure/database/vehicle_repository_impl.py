from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID

from domain.entities.vehicle import Vehicle, VehicleStatus
from domain.repositories.vehicle_repository import VehicleRepository
from infrastructure.database.vehicle_document import VehicleDocument


class VehicleRepositoryImpl(VehicleRepository):
    async def save(self, vehicle: Vehicle) -> Vehicle:
        doc = _to_document(vehicle)
        await doc.insert()
        return vehicle

    async def find_by_id(self, vehicle_id: UUID) -> Vehicle | None:
        doc = await VehicleDocument.find_one(VehicleDocument.id == vehicle_id)
        return _to_entity(doc) if doc else None

    async def update(self, vehicle: Vehicle) -> Vehicle:
        doc = await VehicleDocument.find_one(VehicleDocument.id == vehicle.id)
        if not doc:
            return vehicle
        vehicle.updated_at = datetime.now(UTC)
        await doc.set({
            "brand": vehicle.brand,
            "model": vehicle.model,
            "year": vehicle.year,
            "color": vehicle.color,
            "price": vehicle.price,
            "updated_at": vehicle.updated_at,
        })
        return vehicle

    async def update_status(self, vehicle_id: UUID, status: VehicleStatus) -> Vehicle | None:
        doc = await VehicleDocument.find_one(VehicleDocument.id == vehicle_id)
        if not doc:
            return None
        updated_at = datetime.now(UTC)
        await doc.set({"status": status.value, "updated_at": updated_at})
        doc.status = status.value
        doc.updated_at = updated_at
        return _to_entity(doc)

    async def list_available(self, page: int, page_size: int) -> tuple[list[Vehicle], int]:
        query = VehicleDocument.find(VehicleDocument.status == VehicleStatus.available.value)
        total = await query.count()
        skip = (page - 1) * page_size
        docs = await query.sort("+price").skip(skip).limit(page_size).to_list()
        return [_to_entity(d) for d in docs], total


def _to_document(vehicle: Vehicle) -> VehicleDocument:
    return VehicleDocument(
        id=vehicle.id,
        brand=vehicle.brand,
        model=vehicle.model,
        year=vehicle.year,
        color=vehicle.color,
        price=vehicle.price,
        status=vehicle.status.value,
        created_at=vehicle.created_at,
        updated_at=vehicle.updated_at,
    )


def _to_entity(doc: VehicleDocument) -> Vehicle:
    return Vehicle(
        id=doc.id,
        brand=doc.brand,
        model=doc.model,
        year=doc.year,
        color=doc.color,
        price=Decimal(str(doc.price)),
        status=VehicleStatus(doc.status),
        created_at=doc.created_at,
        updated_at=doc.updated_at,
    )
