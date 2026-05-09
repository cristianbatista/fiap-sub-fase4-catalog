from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class VehicleStatus(str, Enum):
    available = "available"
    sold = "sold"


class Vehicle(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int
    color: str = Field(min_length=1, max_length=50)
    price: Decimal
    status: VehicleStatus = VehicleStatus.available
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        current_year = datetime.now(timezone.utc).year
        if not (1886 <= v <= current_year + 1):
            raise ValueError(
                f"Ano deve estar entre 1886 e {current_year + 1}"
            )
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero")
        return round(v, 2)

    def mark_as_sold(self) -> None:
        if self.status == VehicleStatus.sold:
            raise ValueError("Veículo já está marcado como vendido")
        self.status = VehicleStatus.sold
        self.updated_at = datetime.now(timezone.utc)

    def mark_as_available(self) -> None:
        if self.status == VehicleStatus.available:
            raise ValueError("Veículo já está disponível")
        self.status = VehicleStatus.available
        self.updated_at = datetime.now(timezone.utc)
