from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Attendant(Base):
    __tablename__ = "Attendants"
    user_id: Mapped[str] = mapped_column(String(20), primary_key=True, index=True)
    alloted_slot: Mapped[str] = mapped_column(String(10), nullable=False)

    user = relationship("User", backref="attendant_info")
