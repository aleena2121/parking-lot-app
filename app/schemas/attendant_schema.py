from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict

from app.enums.role_enum import RoleEnum
from app.schemas.user_schema import UserBase


class AttendantBase(UserBase):
    role: Literal[RoleEnum.ATTENDANT] = RoleEnum.ATTENDANT
    alloted_lot: str


class CreateAttendant(AttendantBase):
    password: str


class UpdateAttendant(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)
