from typing import Optional

from sqlalchemy.orm import Session

from app.models.ticket_model import Ticket
from app.models.transaction_model import TransactionModel


def get_transaction_by_ticket(db: Session, ticket_id: str):
    return (
        db.query(TransactionModel)
        .filter(TransactionModel.ticket_id == ticket_id)
        .first()
    )


def get_all_transactions(db: Session, lot_id: Optional[str] = None):
    if lot_id:
        return (
            db.query(TransactionModel)
            .join(Ticket)
            .filter(Ticket.parking_lot_id == lot_id)
            .all()
        )
    return db.query(TransactionModel).all()


def get_transaction_by_id(
    transaction_id: str, db: Session, lot_id: Optional[str] = None
):
    if lot_id:
        return (
            db.query(TransactionModel)
            .join(Ticket)
            .filter(
                TransactionModel.transaction_id == transaction_id,
                Ticket.parking_lot_id == lot_id,
            )
            .first()
        )
    return (
        db.query(TransactionModel)
        .filter(TransactionModel.transaction_id == transaction_id)
        .first()
    )


def get_transaction_by_ticket_id(
    ticket_id: str, db: Session, lot_id: Optional[str] = None
):
    if lot_id:
        return (
            db.query(TransactionModel)
            .join(Ticket)
            .filter(
                TransactionModel.ticket_id == ticket_id, Ticket.parking_lot_id == lot_id
            )
            .first()
        )

    return (
        db.query(TransactionModel)
        .filter(TransactionModel.ticket_id == ticket_id)
        .first()
    )
