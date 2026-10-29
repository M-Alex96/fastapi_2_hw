from datetime import datetime
from pydantic import BaseModel
from typing import Optional
from uuid import UUID

class LoginRequest(BaseModel):
    name: str
    password: str

class LoginResponse(BaseModel):
    id: int
    token: UUID

    class Config:
        from_attributes = True

class CreateUserRequest(BaseModel):
    name: str
    password: str

class CreateUserResponse(BaseModel):
    id: int

class CreateAdvertisementRequest(BaseModel):
    title: str
    description: str
    price: float
    author_id: int

class CreateAdvertisementResponse(BaseModel):
    id: int

class GetUsersResponse(BaseModel):
    id: int
    name: str

class GetAdvertisementsResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author_id: int
    created_at: datetime

class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    password: Optional[str] = None

class UpdateUserResponse(BaseModel):
    id: int
    name: str

class UpdateAdvertisementRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    author_id: Optional[int] = None

class UpdateAdvertisementResponse(BaseModel):
    id: int
    title: str
    description: str
    price: float
    author_id: int
    created_at: datetime

class DeleteUserResponse(BaseModel):
    status: str = "User deleted"

class DeleteAdvertisementResponse(BaseModel):
    status: str = "Advertisement deleted"