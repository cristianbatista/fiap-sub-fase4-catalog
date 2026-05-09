from datetime import UTC, datetime
from decimal import Decimal
from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator


class VehicleStatus(StrEnum):
    available = "available"
    reserved = "reserved"
    sold = "sold"


_ALLOWED_TRANSITIONS: dict[VehicleStatus, set[VehicleStatus]] = {
    VehicleStatus.available: {VehicleStatus.reserved},
    VehicleStatus.reserved: {VehicleStatus.sold, VehicleStatus.available},
    VehicleStatus.sold: set(),
}


class Vehicle(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int
    color: str = Field(min_length=1, max_length=50)
    price: Decimal
    status: VehicleStatus = VehicleStatus.available
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        current_year = datetime.now(UTC).year
        if not (1886 <= v <= current_year + 1):
            raise ValueError(f"Ano deve estar entre 1886 e {current_year + 1}")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero")
        return round(v, 2)

    def _transition_to(self, target: VehicleStatus) -> None:
        allowed = _ALLOWED_TRANSITIONS.get(self.status, set())
        if target not in allowed:
            raise ValueError(
                f"Transição inválida: '{self.status}' → '{target}'"
            )
        self.status = target
        self.updated_at = datetime.now(UTC)

    def mark_as_reserved(self) -> None:
        self._transition_to(VehicleStatus.reserved)

    def mark_as_sold(self) -> None:
        self._transition_to(VehicleStatus.sold)

    def mark_as_available(self) -> None:
        self._transition_to(VehicleStatus.available)
