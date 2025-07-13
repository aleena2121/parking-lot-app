from sqlalchemy.orm import Session

from app.models.transaction_model import TransactionModel


def get_transaction_by_ticket(db: Session, ticket_id: str):
    return (
        db.query(TransactionModel)
        .filter(TransactionModel.ticket_id == ticket_id)
        .first()
    )


def get_all_transactions(db: Session):
    return db.query(TransactionModel).all()


def get_transaction_by_id(transaction_id: str, db: Session):
    return (
        db.query(TransactionModel)
        .filter(TransactionModel.transaction_id == transaction_id)
        .first()
    )


def get_transaction_by_ticket_id(ticket_id: str, db: Session):
    return (
        db.query(TransactionModel)
        .filter(TransactionModel.ticket_id == ticket_id)
        .first()
    )
