from fastapi import status

from main import app
from models import ToDos
from routers.admin import get_db, get_current_user
from .utils import (
    override_get_db,
    override_get_current_user,
    client,
    TestingSessionLocal,
    test_todo
)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_admin(test_todo):
    response = client.get('/admin/todo')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id': 1,
        'complete': False,
        'title': 'Learn to code!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'owner_id': 1,
    }]


def test_delete_todo_admin(test_todo):
    response = client.delete('/admin/todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    todo_object = db.query(ToDos).filter(ToDos.id == 1).first()
    assert todo_object is None


def test_delete_todo_admin_not_found(test_todo):
    response = client.delete('/admin/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        'detail': 'ToDo is not found.'
    }