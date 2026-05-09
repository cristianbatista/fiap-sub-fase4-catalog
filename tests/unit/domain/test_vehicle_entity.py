from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from domain.entities.vehicle import Vehicle, VehicleStatus


def test_vehicle_created_with_status_available():
    v = Vehicle(brand="Toyota", model="Corolla", year=2023, color="Branco", price=Decimal("85000"))
    assert v.status == VehicleStatus.available


def test_vehicle_id_auto_generated():
    v = Vehicle(brand="Toyota", model="Corolla", year=2023, color="Branco", price=Decimal("85000"))
    assert v.id is not None


def test_vehicle_year_minimum_valid():
    v = Vehicle(brand="X", model="Y", year=1886, color="Z", price=Decimal("1"))
    assert v.year == 1886


def test_vehicle_year_current_plus_one_valid():
    current = datetime.now(timezone.utc).year
    v = Vehicle(brand="X", model="Y", year=current + 1, color="Z", price=Decimal("1"))
    assert v.year == current + 1


def test_vehicle_year_below_minimum_raises():
    with pytest.raises(ValidationError) as exc:
        Vehicle(brand="X", model="Y", year=1885, color="Z", price=Decimal("1"))
    assert "1886" in str(exc.value)


def test_vehicle_year_above_maximum_raises():
    current = datetime.now(timezone.utc).year
    with pytest.raises(ValidationError) as exc:
        Vehicle(brand="X", model="Y", year=current + 2, color="Z", price=Decimal("1"))
    assert "Ano" in str(exc.value)


def test_vehicle_price_zero_raises():
    with pytest.raises(ValidationError) as exc:
        Vehicle(brand="X", model="Y", year=2020, color="Z", price=Decimal("0"))
    assert "Preço" in str(exc.value)


def test_vehicle_price_negative_raises():
    with pytest.raises(ValidationError) as exc:
        Vehicle(brand="X", model="Y", year=2020, color="Z", price=Decimal("-100"))
    assert "Preço" in str(exc.value)


def test_vehicle_price_rounded_to_two_decimals():
    v = Vehicle(brand="X", model="Y", year=2020, color="Z", price=Decimal("100.999"))
    assert v.price == Decimal("101.00")


def test_vehicle_mark_as_sold():
    v = Vehicle(brand="X", model="Y", year=2020, color="Z", price=Decimal("1"))
    v.mark_as_sold()
    assert v.status == VehicleStatus.sold


def test_vehicle_mark_as_sold_twice_raises():
    v = Vehicle(brand="X", model="Y", year=2020, color="Z", price=Decimal("1"))
    v.mark_as_sold()
    with pytest.raises(ValueError, match="vendido"):
        v.mark_as_sold()


def test_vehicle_mark_as_available_from_sold():
    v = Vehicle(brand="X", model="Y", year=2020, color="Z", price=Decimal("1"))
    v.mark_as_sold()
    v.mark_as_available()
    assert v.status == VehicleStatus.available


def test_vehicle_mark_as_available_when_already_available_raises():
    v = Vehicle(brand="X", model="Y", year=2020, color="Z", price=Decimal("1"))
    with pytest.raises(ValueError, match="disponível"):
        v.mark_as_available()


def test_vehicle_brand_empty_raises():
    with pytest.raises(ValidationError):
        Vehicle(brand="", model="Y", year=2020, color="Z", price=Decimal("1"))


def test_vehicle_brand_too_long_raises():
    with pytest.raises(ValidationError):
        Vehicle(brand="X" * 101, model="Y", year=2020, color="Z", price=Decimal("1"))


def test_vehicle_color_too_long_raises():
    with pytest.raises(ValidationError):
        Vehicle(brand="X", model="Y", year=2020, color="Z" * 51, price=Decimal("1"))
