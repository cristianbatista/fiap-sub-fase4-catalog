import pytest
from pydantic import ValidationError

from presentation.schemas.status_schemas import StatusUpdateRequest, StatusValue


def test_status_update_request_sold():
    req = StatusUpdateRequest(status="sold")
    assert req.status == StatusValue.sold


def test_status_update_request_available():
    req = StatusUpdateRequest(status="available")
    assert req.status == StatusValue.available


def test_status_update_request_invalid_raises():
    with pytest.raises(ValidationError):
        StatusUpdateRequest(status="unknown")
