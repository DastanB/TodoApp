from typing import Annotated

from fastapi import APIRouter, Path, HTTPException, Depends
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from starlette import status

from models import Users
from database import SessionLocal
from requests.auth import UpdateUserRequest
from requests.users import ChangePasswordRequest
from .auth import get_current_user

router = APIRouter(
    prefix='/users',
    tags=['users'],
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]

user_dependency = Annotated[dict, Depends(get_current_user)]

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


@router.get('/profile', status_code=status.HTTP_200_OK)
async def get_user(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    return db.query(Users).filter(Users.id == user.get('id')).first()


@router.put('/change-password', status_code=status.HTTP_204_NO_CONTENT)
async def change_user_password(
        user: user_dependency,
        db: db_dependency,
        change_password_request: ChangePasswordRequest
):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    user_object = db.query(Users).filter(Users.id == user.get('id')).first()
    if not user_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    if not bcrypt_context.verify(change_password_request.password, user_object.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Error on passwords')

    user_object.hashed_password = bcrypt_context.hash(change_password_request.new_password)

    db.add(user_object)
    db.commit()


@router.put('/', status_code=status.HTTP_204_NO_CONTENT)
async def update_user(user: user_dependency, db: db_dependency, update_user_request: UpdateUserRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')

    user_object = db.query(Users).filter(Users.id == user.get('id')).first()
    if not user_object:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='User not found')

    user_object.email = update_user_request.email
    user_object.username = update_user_request.username
    user_object.first_name = update_user_request.first_name
    user_object.last_name = update_user_request.last_name
    user_object.phone_number = update_user_request.phone_number

    db.add(user_object)
    db.commit()
