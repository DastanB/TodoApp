from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status

from models import ToDos
from requests.todos import ToDoRequest
from database import SessionLocal
from .auth import get_current_user

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]


@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    return db.query(ToDos).filter(ToDos.owner_id == user.get('id')).all()


@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
async def get_todo_by_id(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo_object = db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get('id')).first()

    if todo_object is not None:
        return todo_object
    else:
        raise HTTPException(404, 'ToDo is not found.')


@router.post('/todo', status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: ToDoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo_object = ToDos(**todo_request.model_dump(), owner_id=user.get('id'))

    db.add(todo_object)
    db.commit()


@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(
        user: user_dependency,
        db: db_dependency,
        todo_request: ToDoRequest,
        todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo_obejct = db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get('id')).first()
    if todo_obejct is None:
        raise HTTPException(404, 'ToDo is not found.')

    todo_obejct.title = todo_request.title
    todo_obejct.description = todo_request.description
    todo_obejct.priority = todo_request.priority
    todo_obejct.complete = todo_request.complete

    db.add(todo_obejct)
    db.commit()


@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(
        user: user_dependency,
        db: db_dependency,
        todo_id: int = Path(gt=0),
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo_object = db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get('id')).first()
    if todo_object is None:
        raise HTTPException(404, 'ToDo is not found.')

    db.query(ToDos).filter(ToDos.id == todo_id).filter(ToDos.owner_id == user.get('id')).delete()
    db.commit()
