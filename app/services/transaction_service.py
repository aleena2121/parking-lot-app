from sqlalchemy.orm import Session

from app.models.transaction_model import TransactionModel
from app.schemas.ticket_schema import ShowTicket


def calculate_amount(ticket: ShowTicket):
    duration = max(1, (ticket.exit_time - ticket.entry_time).total_seconds()) // 3600
    return 20.0 * duration


def create_transaction(db: Session, ticket):
    amount = calculate_amount(ticket=ticket)

    new_transaction = TransactionModel(
        ticket_id=ticket.ticket_id,
        amount=amount,
        payment_status="PENDING",
    )
    db.add(new_transaction)

    return new_transaction
