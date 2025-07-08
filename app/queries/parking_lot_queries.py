from sqlalchemy.orm import Session

from app.models.parking_lot_model import ParkingLot


def get_lot_by_id(db: Session, lot_id: str):
    return db.query(ParkingLot).filter(ParkingLot.parking_lot_id == lot_id).first()


def get_all_lots(db: Session):
    return db.query(ParkingLot).all()
