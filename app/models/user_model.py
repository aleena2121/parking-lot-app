from datetime import datetime

from sqlalchemy import DateTime
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy import String, event, text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base
from app.enums.role_enum import RoleEnum


class User(Base):
    __tablename__ = "users"
    user_id: Mapped[str] = mapped_column(String(20), primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    email: Mapped[str] = mapped_column(String(100), nullable=False)
    password: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(default=datetime.now)
    role: Mapped[RoleEnum] = mapped_column(
        SQLAlchemyEnum(RoleEnum, name="roleenum"), nullable=False
    )


@event.listens_for(User, "before_insert")
def get_user_id(mapper, connection, target):
    result = connection.execute(
        text(
            "SELECT user_id FROM users ORDER BY CAST(SUBSTRING(user_id FROM 5) AS INTEGER) DESC LIMIT 1"
        )
    ).first()

    if result is None:
        next_num = 1
    else:
        last_id = result[0]
        last_num = int(last_id.replace("USER", ""))
        next_num = last_num + 1

    target.user_id = f"USER{next_num}"
