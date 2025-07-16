from typing import Optional

from sqlalchemy.orm import Session

from app.config.logger_config import func_logger
from app.models.slot_model import Slot
from app.models.ticket_model import Ticket


def get_ticket_by_id(db: Session, ticket_id: str, lot_id: Optional[str] = None):
    if not lot_id:
        return db.query(Ticket).filter(Ticket.ticket_id == ticket_id).first()
    else:
        return (
            db.query(Ticket)
            .filter(Ticket.ticket_id == ticket_id, Ticket.parking_lot_id == lot_id)
            .first()
        )


def get_all_tickets(db: Session, lot_id: Optional[str] = None):
    if not lot_id:
        return db.query(Ticket).all()
    else:
        return db.query(Ticket).filter(Ticket.parking_lot_id == lot_id).all()


def get_ticket_by_lot_id(db: Session, lot_id: str):
    return db.query(Ticket).filter(Ticket.parking_lot_id == lot_id).all()


def get_ticket_by_lot_id_and_slot_name(db: Session, lot_id: str, slot_name: str):
    func_logger.info(f"Searching for slot with name={slot_name}, lot_id={lot_id}")
    slot = (
        db.query(Slot)
        .filter(Slot.parking_lot_id == lot_id, Slot.slot_name == slot_name)
        .first()
    )

    if not slot:
        return []
    return (
        db.query(Ticket)
        .filter(Ticket.parking_lot_id == lot_id, Ticket.slot_id == slot.slot_id)
        .all()
    )
