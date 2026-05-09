from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from beanie import Document
from bson import Decimal128
from pydantic import Field, field_validator
from pymongo import ASCENDING, IndexModel


class VehicleDocument(Document):
    id: UUID = Field(default_factory=uuid4)
    brand: str
    model: str
    year: int
    color: str
    price: Decimal

    @field_validator("price", mode="before")
    @classmethod
    def coerce_decimal128(cls, v: object) -> object:
        if isinstance(v, Decimal128):
            return Decimal(str(v))
        return v
    status: str = "available"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    class Settings:
        name = "vehicles"
        indexes = [
            IndexModel([("status", ASCENDING), ("price", ASCENDING)]),
            IndexModel([("price", ASCENDING)]),
        ]
