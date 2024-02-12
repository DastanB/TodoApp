import pytest
from fastapi import status, HTTPException
from jose import jwt
from datetime import timedelta

from main import app
from routers.auth import (
    get_db,
    authenticate_user,
    create_access_token,
    SECRET_KEY,
    ALGORITHM,
    get_current_user,
)
from .utils import (
    override_get_db,
    client,
    test_user,
    TestingSessionLocal
)

app.dependency_overrides[get_db] = override_get_db


def test_authenticate_user(test_user):
    db = TestingSessionLocal()

    authenticated_user = authenticate_user(test_user.username, '1234', db)
    assert authenticated_user is not None
    assert authenticated_user.username == test_user.username

    non_existing_authenticated_user = authenticate_user('test', '1234', db)
    assert non_existing_authenticated_user is None

    wrong_password_authenticated_user = authenticate_user(test_user.username, '124', db)
    assert wrong_password_authenticated_user is None


def test_create_access_token():
    username = 'testdastan'
    user_id = 1
    role = 'user'
    expires_delta = timedelta(days=1)

    token = create_access_token(username, user_id, role, expires_delta)
    decoded_token = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={'verify_signature': False})

    assert decoded_token['sub'] == username
    assert decoded_token['id'] == user_id
    assert decoded_token['role'] == role


@pytest.mark.asyncio
async def test_get_current_user_valid_token():
    encode = {
        'sub': 'testdastan',
        'id': 1,
        'role': 'admin'
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
    user = await get_current_user(token)

    assert user == {'username': 'testdastan', 'id': 1, 'role': 'admin'}


@pytest.mark.asyncio
async def test_get_current_user_valid_token_missing_payload():
    encode = {
        'role': 'admin'
    }
    token = jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)

    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(token)

    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == 'Could not validate user.'