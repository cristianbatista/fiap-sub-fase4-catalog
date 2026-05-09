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


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=VehicleResponse,
    summary="Registrar veículo",
    description=(
        "Cadastra um novo veículo no catálogo com status inicial **available**. "
        "Requer autenticação Bearer. Retorna o veículo criado com ID único gerado automaticamente."
    ),
    responses={
        201: {"description": "Veículo criado com sucesso"},
        401: {"description": "Token ausente ou inválido"},
        422: {"description": "Campos inválidos ou ausentes"},
    },
)
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


@router.get(
    "",
    status_code=status.HTTP_200_OK,
    response_model=VehicleListResponse,
    summary="Listar veículos disponíveis",
    description=(
        "Retorna todos os veículos com status **available**, ordenados por preço crescente. "
        "Suporta paginação via `page` e `page_size` (máximo 100 itens por página)."
    ),
    responses={
        200: {"description": "Lista de veículos disponíveis"},
        401: {"description": "Token ausente ou inválido"},
    },
)
async def list_vehicles(
    page: int = Query(default=1, ge=1, description="Página (1-indexed)"),
    page_size: int = Query(default=20, ge=1, le=100, description="Itens por página (máximo 100)"),
    current_user: dict = Depends(get_current_user),
    repository: VehicleRepositoryImpl = Depends(_get_repository),
):
    use_case = ListAvailableVehicles(repository)
    items, total = await use_case.execute(page=page, page_size=page_size)
    return VehicleListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get(
    "/{vehicle_id}",
    status_code=status.HTTP_200_OK,
    response_model=VehicleResponse,
    summary="Obter veículo por ID",
    description="Retorna os dados completos de um veículo pelo seu identificador único.",
    responses={
        200: {"description": "Dados do veículo"},
        401: {"description": "Token ausente ou inválido"},
        404: {"description": "Veículo não encontrado"},
    },
)
async def get_vehicle(
    vehicle_id: UUID,
    current_user: dict = Depends(get_current_user),
    repository: VehicleRepositoryImpl = Depends(_get_repository),
):
    use_case = GetVehicle(repository)
    try:
        vehicle = await use_case.execute(vehicle_id)
    except GetNotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado.",
        ) from err
    return vehicle


@router.put(
    "/{vehicle_id}",
    status_code=status.HTTP_200_OK,
    response_model=VehicleResponse,
    summary="Atualizar dados do veículo",
    description=(
        "Atualiza todos os atributos editáveis de um veículo existente. "
        "Todos os campos são obrigatórios. O status do veículo é preservado."
    ),
    responses={
        200: {"description": "Veículo atualizado com sucesso"},
        401: {"description": "Token ausente ou inválido"},
        404: {"description": "Veículo não encontrado"},
        422: {"description": "Campos inválidos"},
    },
)
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
    except NotFoundError as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado.",
        ) from err
    return vehicle
