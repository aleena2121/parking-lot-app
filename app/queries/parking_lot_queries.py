from sqlalchemy.orm import Session

from app.models.parking_lot_model import ParkingLot
from app.models.slot_model import Slot


def get_lot_by_id(db: Session, lot_id: str):
    return db.query(ParkingLot).filter(ParkingLot.parking_lot_id == lot_id).first()


def get_all_lots(db: Session):
    return db.query(ParkingLot).all()


def get_slot_by_id(db: Session, slot_id: str):
    return db.query(Slot).filter(Slot.slot_id == slot_id).first()


def get_slot_name(db: Session, slot_id: str):
    return db.query(Slot).filter(Slot.slot_id == slot_id).first()
