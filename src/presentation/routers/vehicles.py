from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse

from application.use_cases.create_vehicle import CreateVehicle
from infrastructure.auth.oauth2 import get_current_user
from infrastructure.database.vehicle_repository_impl import VehicleRepositoryImpl
from presentation.schemas.vehicle_schemas import VehicleCreateRequest, VehicleResponse

router = APIRouter()


def _get_repository() -> VehicleRepositoryImpl:
    return VehicleRepositoryImpl()


@router.post("", status_code=status.HTTP_201_CREATED, response_model=VehicleResponse)
async def create_vehicle(
    payload: VehicleCreateRequest,
    current_user: dict = Depends(get_current_user),
    repository: VehicleRepositoryImpl = Depends(_get_repository),
):
    use_case = CreateVehicle(repository)
    vehicle = await use_case.execute(
        brand=payload.brand,
        model=payload.model,
        year=payload.year,
        color=payload.color,
        price=payload.price,
    )
    return vehicle
