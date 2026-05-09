from datetime import datetime, timezone
from decimal import Decimal
from uuid import UUID, uuid4

from beanie import Document, Indexed
from pydantic import Field
from pymongo import ASCENDING, IndexModel


class VehicleDocument(Document):
    id: UUID = Field(default_factory=uuid4)
    brand: str
    model: str
    year: int
    color: str
    price: Decimal
    status: str = "available"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Settings:
        name = "vehicles"
        indexes = [
            IndexModel([("status", ASCENDING), ("price", ASCENDING)]),
            IndexModel([("price", ASCENDING)]),
        ]
