from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class Row(Base):
    __tablename__ = "rows"
    __table_args__ = (
        PrimaryKeyConstraint("parking_lot_id", "row_label", name="pk_lot_row"),
    )
    parking_lot_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("parkinglots.parking_lot_id"), nullable=False
    )
    row_label: Mapped[str] = mapped_column(String(20), nullable=False)
    parking_lot = relationship("ParkingLot", back_populates="rows")
