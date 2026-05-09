import os
from unittest.mock import patch

import pytest
from fastapi import HTTPException
from jose import JWTError

os.environ.setdefault("JWT_SECRET_KEY", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")


@pytest.mark.asyncio
async def test_get_current_user_valid_token_returns_payload():
    from infrastructure.auth.oauth2 import get_current_user

    with patch("infrastructure.auth.oauth2.jwt.decode", return_value={"sub": "user1"}):
        result = await get_current_user("valid-token")

    assert result == {"sub": "user1"}


@pytest.mark.asyncio
async def test_get_current_user_invalid_token_raises_401():
    from infrastructure.auth.oauth2 import get_current_user

    with (
        patch(
            "infrastructure.auth.oauth2.jwt.decode", side_effect=JWTError("bad token")
        ),
        pytest.raises(HTTPException) as exc,
    ):
        await get_current_user("bad-token")

    assert exc.value.status_code == 401
    assert "inválidas" in exc.value.detail


@pytest.mark.asyncio
async def test_get_current_user_missing_sub_raises_401():
    from infrastructure.auth.oauth2 import get_current_user

    with (
        patch("infrastructure.auth.oauth2.jwt.decode", return_value={"data": "no-sub"}),
        pytest.raises(HTTPException) as exc,
    ):
        await get_current_user("token-without-sub")

    assert exc.value.status_code == 401
