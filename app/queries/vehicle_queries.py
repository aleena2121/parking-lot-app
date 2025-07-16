from typing import Optional

from sqlalchemy.orm import Session

from app.models.ticket_model import Ticket
from app.models.vehicle_model import Vehicle


def get_vehicle_by_id(db: Session, vehicle_id: str, lot_id: Optional[str] = None):
    if lot_id:
        return (
            db.query(Vehicle)
            .join(Ticket)
            .filter(Vehicle.vehicle_id == vehicle_id, Ticket.parking_lot_id == lot_id)
            .first()
        )

    return db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()


def get_vehicle_by_plate_no(db: Session, plate_no: str, lot_id: Optional[str] = None):
    if lot_id:
        return (
            db.query(Vehicle)
            .join(Ticket)
            .filter(Vehicle.plate_number == plate_no, Ticket.parking_lot_id == lot_id)
            .first()
        )
    return db.query(Vehicle).filter(Vehicle.plate_number == plate_no).first()


def get_all_vehicles(db: Session, lot_id: Optional[str] = None):
    if lot_id:
        return (
            db.query(Vehicle).join(Ticket).filter(Ticket.parking_lot_id == lot_id).all()
        )
    return db.query(Vehicle).all()


def get_active_vehicles_in_lot(db: Session, lot_id: str):
    return (
        db.query(Vehicle)
        .join(Ticket)
        .filter(Ticket.parking_lot_id == lot_id, Ticket.is_active == True)
    )
