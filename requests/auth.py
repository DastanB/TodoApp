from pydantic import BaseModel, Field


class CreateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str
    phone_number: str


class UpdateUserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    phone_number: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str
