from sqlalchemy.orm import Session

from app.models.vehicle_model import Vehicle


def get_vehicle_by_id(db: Session, vehicle_id: str):
    return db.query(Vehicle).filter(Vehicle.vehicle_id == vehicle_id).first()


def get_vehicle_by_plate_no(db: Session, plate_no: str):
    return db.query(Vehicle).filter(Vehicle.plate_number == plate_no).first()


def get_all_vehicles(db: Session):
    return db.query(Vehicle).all()
