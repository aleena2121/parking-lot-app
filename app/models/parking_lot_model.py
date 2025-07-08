from sqlalchemy import JSON, Boolean, Integer, String, event, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class ParkingLot(Base):
    __tablename__ = "parkinglots"

    parking_lot_id: Mapped[str] = mapped_column(
        String(20), primary_key=True, index=True
    )
    capacity: Mapped[int] = mapped_column(Integer, nullable=False)
    available_slots: Mapped[list[str]] = mapped_column(
        JSON, nullable=False, default=list
    )
    is_full: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    rows = relationship("Row", back_populates="parking_lot")
    slots = relationship("Slot", back_populates="parking_lot")


@event.listens_for(ParkingLot, "before_insert")
def get_commission_id(mapper, connection, target):
    result = connection.execute(
        text(
            "SELECT parking_lot_id FROM parkinglots ORDER BY CAST(SUBSTRING(parking_lot_id FROM 3) AS INTEGER) DESC LIMIT 1"
        )
    ).first()

    if result is None:
        next_num = 1
    else:
        last_id = result[0]
        last_num = int(last_id.replace("PL", ""))
        next_num = last_num + 1

    target.parking_lot_id = f"PL{next_num}"
