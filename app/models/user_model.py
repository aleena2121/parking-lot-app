from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums.role_enum import RoleEnum


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[str] = mapped_column(String(20), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    role: Mapped[RoleEnum] = mapped_column(
        SQLAlchemyEnum(RoleEnum, name="roleEnum"), nullable=False
    )
