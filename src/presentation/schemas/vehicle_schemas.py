from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


def _current_year() -> int:
    return datetime.now().year


class VehicleCreateRequest(BaseModel):
    brand: str = Field(min_length=1, max_length=100)
    model: str = Field(min_length=1, max_length=100)
    year: int
    color: str = Field(min_length=1, max_length=50)
    price: Decimal

    @field_validator("brand", "model", "color", mode="before")
    @classmethod
    def not_blank(cls, v: str) -> str:
        if not str(v).strip():
            raise ValueError("Campo não pode estar em branco")
        return v

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int) -> int:
        current = _current_year()
        if not (1886 <= v <= current + 1):
            raise ValueError(f"Ano deve estar entre 1886 e {current + 1}")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal) -> Decimal:
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero")
        return v

    model_config = {"json_schema_extra": {"example": {
        "brand": "Toyota",
        "model": "Corolla",
        "year": 2023,
        "color": "Branco",
        "price": "85000.00",
    }}}


class VehicleUpdateRequest(BaseModel):
    brand: str | None = Field(default=None, min_length=1, max_length=100)
    model: str | None = Field(default=None, min_length=1, max_length=100)
    year: int | None = None
    color: str | None = Field(default=None, min_length=1, max_length=50)
    price: Decimal | None = None

    @field_validator("year")
    @classmethod
    def validate_year(cls, v: int | None) -> int | None:
        if v is None:
            return v
        current = _current_year()
        if not (1886 <= v <= current + 1):
            raise ValueError(f"Ano deve estar entre 1886 e {current + 1}")
        return v

    @field_validator("price")
    @classmethod
    def validate_price(cls, v: Decimal | None) -> Decimal | None:
        if v is None:
            return v
        if v <= 0:
            raise ValueError("Preço deve ser maior que zero")
        return v


class VehicleResponse(BaseModel):
    id: UUID
    brand: str
    model: str
    year: int
    color: str
    price: Decimal
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class VehicleListResponse(BaseModel):
    items: list[VehicleResponse]
    total: int
    page: int
    page_size: int
