from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.enums.role_enum import RoleEnum


class UserBase(BaseModel):
    name: str
    email: str
    role: RoleEnum

    model_config = ConfigDict(from_attributes=True)


class CreateUser(UserBase):
    password: str


class UpdateUser(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    role: Optional[RoleEnum] = None

    model_config = ConfigDict(from_attributes=True)


class ShowUser(UserBase):
    user_id: str
