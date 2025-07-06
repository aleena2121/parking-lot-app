from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Attendant(Base):
    __tablename__ = "attendants"
    user_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("users.user_id"), primary_key=True, index=True
    )
    alloted_lot: Mapped[str] = mapped_column(String(10), nullable=True)

    user = relationship("User", backref="attendant_info")
