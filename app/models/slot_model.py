from sqlalchemy import Boolean
from sqlalchemy import Enum as SQLAEnum
from sqlalchemy import ForeignKey, ForeignKeyConstraint, String, event, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base
from app.enums.slot_enum import SlotEnum


class Slot(Base):
    __tablename__ = "slots"
    __table_args__ = (
        ForeignKeyConstraint(
            ["parking_lot_id", "row_label"], ["rows.parking_lot_id", "rows.row_label"]
        ),
    )
    slot_id: Mapped[str] = mapped_column(
        String(20), index=True, primary_key=True, nullable=False
    )
    slot_name: Mapped[str] = mapped_column(String(20), nullable=False)
    parking_lot_id: Mapped[str] = mapped_column(
        String(20), ForeignKey("parkinglots.parking_lot_id"), nullable=False
    )
    row_label: Mapped[str] = mapped_column(String(20), nullable=False)
    is_occupied: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    slot_category: Mapped[SlotEnum] = mapped_column(
        SQLAEnum(SlotEnum, name="slotenum"), nullable=False
    )
    parking_lot = relationship("ParkingLot", back_populates="slots")


@event.listens_for(Slot, "before_insert")
def get_commission_id(mapper, connection, target):
    result = connection.execute(
        text(
            "SELECT slot_id FROM slots ORDER BY CAST(SUBSTRING(slot_id FROM 3) AS INTEGER) DESC LIMIT 1"
        )
    ).first()

    if result is None:
        next_num = 1
    else:
        last_id = result[0]
        last_num = int(last_id.replace("SL", ""))
        next_num = last_num + 1

    target.slot_id = f"SL{next_num}"
