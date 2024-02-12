from fastapi import status

from main import app
from models import ToDos
from routers.todos import get_db, get_current_user
from .utils import (
    override_get_db,
    override_get_current_user,
    client,
    TestingSessionLocal,
    test_todo
)

app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_read_all_authenticated(test_todo):
    response = client.get('/')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [{
        'id': 1,
        'complete': False,
        'title': 'Learn to code!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'owner_id': 1,
    }]


def test_read_one_authenticated(test_todo):
    response = client.get('/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': 1,
        'complete': False,
        'title': 'Learn to code!',
        'description': 'Need to learn everyday!',
        'priority': 5,
        'owner_id': 1,
    }


def test_read_one_authenticated_not_found(test_todo):
    response = client.get('/todo/2')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        'detail': 'ToDo is not found.'
    }


def test_create_todo(test_todo):
    body = {
        'title': 'New todo!',
        'description': 'New todo description.',
        'complete': False,
        'priority': 5,
    }

    response = client.post('/todo/', json=body)
    assert response.status_code == status.HTTP_201_CREATED

    db = TestingSessionLocal()
    todo_object = db.query(ToDos).filter(ToDos.id == 2).first()
    assert todo_object.title == body.get('title')
    assert todo_object.description == body.get('description')
    assert todo_object.complete == body.get('complete')
    assert todo_object.priority == body.get('priority')


def test_update_todo(test_todo):
    body = {
        'title': 'Change title!',
        'description': 'Updated todo description.',
        'complete': False,
        'priority': 5,
    }

    response = client.put('/todo/1', json=body)
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    todo_object = db.query(ToDos).filter(ToDos.id == 1).first()
    assert todo_object.title == body.get('title')
    assert todo_object.description == body.get('description')
    assert todo_object.complete == body.get('complete')
    assert todo_object.priority == body.get('priority')


def test_update_todo_not_found(test_todo):
    body = {
        'title': 'Change title!',
        'description': 'Updated todo description.',
        'complete': False,
        'priority': 5,
    }

    response = client.put('/todo/999', json=body)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        'detail': 'ToDo is not found.'
    }


def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT

    db = TestingSessionLocal()
    todo_object = db.query(ToDos).filter(ToDos.id == 1).first()
    assert todo_object is None


def test_delete_todo_not_found(test_todo):
    response = client.delete('/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {
        'detail': 'ToDo is not found.'
    }

