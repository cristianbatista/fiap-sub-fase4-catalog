from enum import Enum

from pydantic import BaseModel


class StatusValue(str, Enum):
    available = "available"
    sold = "sold"


class StatusUpdateRequest(BaseModel):
    status: StatusValue
