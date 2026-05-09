from enum import StrEnum

from pydantic import BaseModel


class StatusValue(StrEnum):
    available = "available"
    sold = "sold"


class StatusUpdateRequest(BaseModel):
    status: StatusValue
