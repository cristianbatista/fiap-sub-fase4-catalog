from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from application.use_cases.create_vehicle import CreateVehicle
from application.use_cases.get_vehicle import GetVehicle
from application.use_cases.get_vehicle import NotFoundError as GetNotFoundError
from application.use_cases.list_available_vehicles import ListAvailableVehicles
from application.use_cases.update_vehicle import NotFoundError, UpdateVehicle
from infrastructure.auth.oauth2 import get_current_user
from infrastructure.database.vehicle_repository_impl import VehicleRepositoryImpl
from presentation.schemas.vehicle_schemas import (
    VehicleCreateRequest,
    VehicleListResponse,
    VehicleResponse,
    VehicleUpdateRequest,
)

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


@router.get("", status_code=status.HTTP_200_OK, response_model=VehicleListResponse)
async def list_vehicles(
    page: int = Query(default=1, ge=1, description="Página (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Itens por página (máximo 100)"),
    current_user: dict = Depends(get_current_user),
    repository: VehicleRepositoryImpl = Depends(_get_repository),
):
    use_case = ListAvailableVehicles(repository)
    items, total = await use_case.execute(page=page, page_size=page_size)
    return VehicleListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/{vehicle_id}", status_code=status.HTTP_200_OK, response_model=VehicleResponse)
async def get_vehicle(
    vehicle_id: UUID,
    current_user: dict = Depends(get_current_user),
    repository: VehicleRepositoryImpl = Depends(_get_repository),
):
    use_case = GetVehicle(repository)
    try:
        vehicle = await use_case.execute(vehicle_id)
    except GetNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado.",
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
