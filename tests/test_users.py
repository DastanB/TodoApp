from fastapi import status

from main import app
from routers.users import get_db, get_current_user
from .utils import (
    override_get_db,
    override_get_current_user,
    client,
    test_user
)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_get_user_info(test_user):
    response = client.get('/users/profile')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['id'] == 1
    assert response.json()['username'] == 'test_dastan'
    assert response.json()['email'] == 'dastan211298@gmail.com'
    assert response.json()['first_name'] == 'Dastan'
    assert response.json()['last_name'] == 'Baitursynov'
    assert response.json()['role'] == 'admin'
    assert response.json()['phone_number'] == '87772107915'
    assert response.json()['is_active'] is True


def test_change_password_success(test_user):
    response = client.put('/users/change-password', json={'password': '1234', 'new_password': '12345'})
    assert response.status_code == status.HTTP_204_NO_CONTENT


def test_change_password_fail(test_user):
    response = client.put('/users/change-password', json={'password': '123', 'new_password': '12345'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Error on passwords'}


def test_user_update(test_user):
    body = {
        'email': 'dastan211298@gmail.com',
        'username': 'test_dastan',
        'first_name': 'Dastan',
        'last_name': 'Baitursynov',
        'phone_number': '87772107915'
    }

    response = client.put('/users/', json=body)
    assert response.status_code == status.HTTP_204_NO_CONTENT

