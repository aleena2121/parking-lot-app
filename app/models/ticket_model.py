from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlalchemy import (TIMESTAMP, Boolean, ForeignKey, Integer, String, event,
                        text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.slot_model import Slot
    from app.models.transaction_model import TransactionModel
    from app.models.vehicle_model import Vehicle


class Ticket(Base):
    __tablename__ = "tickets"

    ticket_id: Mapped[str] = mapped_column(primary_key=True, index=True)
    vehicle_id: Mapped[str] = mapped_column(
        ForeignKey("vehicles.vehicle_id"), nullable=False
    )
    parking_lot_id: Mapped[str] = mapped_column(
        ForeignKey("parkinglots.parking_lot_id"), nullable=False
    )
    slot_id: Mapped[str] = mapped_column(ForeignKey("slots.slot_id"), nullable=False)
    attendant_id: Mapped[str] = mapped_column(
        ForeignKey("attendants.user_id"), nullable=False
    )
    entry_time: Mapped[datetime] = mapped_column(
        TIMESTAMP, default=datetime.now(timezone.utc), nullable=False
    )
    exit_time: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    vehicle = relationship("Vehicle", back_populates="tickets")
    slot = relationship("Slot", back_populates="tickets")

    transaction = relationship(
        "TransactionModel", back_populates="ticket", uselist=False
    )


@event.listens_for(Ticket, "before_insert")
def get_ticket_id(mapper, connection, target):
    result = connection.execute(
        text(
            "SELECT ticket_id FROM tickets ORDER BY CAST(SUBSTRING(ticket_id FROM 3) AS INTEGER) DESC LIMIT 1"
        )
    ).first()

    if result is None:
        next_num = 1
    else:
        last_id = result[0]
        last_num = int(last_id.replace("TI", ""))
        next_num = last_num + 1

    target.ticket_id = f"TI{next_num}"
