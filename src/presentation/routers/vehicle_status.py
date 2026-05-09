from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from application.use_cases.update_vehicle_status import ConflictError, NotFoundError, UpdateVehicleStatus
from domain.entities.vehicle import VehicleStatus
from infrastructure.auth.oauth2 import get_current_user
from infrastructure.database.vehicle_repository_impl import VehicleRepositoryImpl
from presentation.schemas.status_schemas import StatusUpdateRequest

router = APIRouter()


class StatusResponse(BaseModel):
    id: UUID
    status: str
    updated_at: datetime


def _get_repository() -> VehicleRepositoryImpl:
    return VehicleRepositoryImpl()


@router.patch(
    "/{vehicle_id}/status",
    status_code=status.HTTP_200_OK,
    response_model=StatusResponse,
    summary="Atualizar status do veículo",
    description=(
        "Atualiza o status do ciclo de vida de um veículo. "
        "Utilizado exclusivamente pelo **Sales Service** para marcar veículos como **sold** "
        "(na iniciação de uma venda) ou restaurar para **available** (no cancelamento do pagamento). "
        "Transições redundantes (ex: sold → sold) retornam HTTP 409."
    ),
    responses={
        200: {"description": "Status atualizado com sucesso"},
        401: {"description": "Token ausente ou inválido"},
        404: {"description": "Veículo não encontrado"},
        409: {"description": "Conflito — transição de status inválida ou redundante"},
        422: {"description": "Valor de status inválido"},
    },
)
async def update_vehicle_status(
    vehicle_id: UUID,
    payload: StatusUpdateRequest,
    current_user: dict = Depends(get_current_user),
    repository: VehicleRepositoryImpl = Depends(_get_repository),
):
    use_case = UpdateVehicleStatus(repository)
    try:
        vehicle = await use_case.execute(vehicle_id, VehicleStatus(payload.status.value))
    except NotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Veículo não encontrado.",
        )
    except ConflictError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Conflito de status: transição inválida ou redundante.",
        )
    return StatusResponse(id=vehicle.id, status=vehicle.status.value, updated_at=vehicle.updated_at)
