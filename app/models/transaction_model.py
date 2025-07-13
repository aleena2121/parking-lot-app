from datetime import datetime

from sqlalchemy import (TIMESTAMP, ForeignKey, Integer, Numeric, String, event,
                        text)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class TransactionModel(Base):
    __tablename__ = "transactions"

    transaction_id: Mapped[str] = mapped_column(primary_key=True, index=True)
    ticket_id: Mapped[str] = mapped_column(
        ForeignKey("tickets.ticket_id"), nullable=False
    )
    payment_timestamp: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=True)
    amount: Mapped[float] = mapped_column(Numeric(10, 2), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(50), nullable=False)

    ticket = relationship("Ticket", back_populates="transaction")


@event.listens_for(TransactionModel, "before_insert")
def get_transaction_id(mapper, connection, target):
    result = connection.execute(
        text(
            "SELECT transaction_id FROM transactions ORDER BY CAST(SUBSTRING(transaction_id FROM 3) AS INTEGER) DESC LIMIT 1"
        )
    ).first()

    if result is None:
        next_num = 1
    else:
        last_id = result[0]
        last_num = int(last_id.replace("TR", ""))
        next_num = last_num + 1

    target.transaction_id = f"TR{next_num}"
