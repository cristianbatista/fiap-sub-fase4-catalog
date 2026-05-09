from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from application.use_cases.create_vehicle import CreateVehicle
from application.use_cases.update_vehicle import NotFoundError, UpdateVehicle
from infrastructure.auth.oauth2 import get_current_user
from infrastructure.database.vehicle_repository_impl import VehicleRepositoryImpl
from presentation.schemas.vehicle_schemas import VehicleCreateRequest, VehicleResponse, VehicleUpdateRequest

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


@router.put("/{vehicle_id}", status_code=status.HTTP_200_OK, response_model=VehicleResponse)
async def update_vehicle(
    vehicle_id: UUID,
    payload: VehicleUpdateRequest,
    current_user: dict = Depends(get_current_user),
    repository: VehicleRepositoryImpl = Depends(_get_repository),
):
    use_case = UpdateVehicle(repository)
    try:
        vehicle = await use_case.execute(
            vehicle_id=vehicle_id,
            brand=payload.brand,
            model=payload.model,
            year=payload.year,
            color=payload.color,
            price=payload.price,
        )
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado.",
        )
    return vehicle
