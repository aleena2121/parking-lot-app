from fastapi import Depends, status
from sqlalchemy.orm import Session

from app.config.logger_config import func_logger
from app.db.session import get_db
from app.exceptions import parking_lot_exceptions
from app.models.parking_lot_model import ParkingLot
from app.models.slot_model import Slot
from app.models.vehicle_model import Vehicle
from app.queries.vehicle_queries import get_vehicle_by_plate_no
from app.schemas.response_schema import StandardResponse
from app.schemas.ticket_schema import TicketBase
from app.schemas.vehicle_schema import VehicleBase


def add_or_update_vehicle(request: VehicleBase, db: Session = Depends(get_db)):
    vehicle = get_vehicle_by_plate_no(db, request.plate_number)

    if vehicle:
        for field, value in request.model_dump().items():
            setattr(vehicle, field, value)
    else:
        vehicle = Vehicle(**request.model_dump())
        db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    func_logger.info(f"Vehicle Registered, ID: {vehicle.vehicle_id}")
    return StandardResponse(
        message="Vehicle registered",
        payload=vehicle,
        status_code=status.HTTP_201_CREATED,
    )


def get_slot(request: TicketBase, db: Session, parking_lot_id: str):
    parking_lot = (
        db.query(ParkingLot).filter(ParkingLot.parking_lot_id == parking_lot_id).first()
    )
    if parking_lot.is_full:
        raise parking_lot_exceptions.ParkingLotFullException()

    vehicle_type = request.vehicle_category
    driver_type = request.driver_category

    if vehicle_type == "Large":
        category = "Large"
    elif driver_type == "Handicapped":
        category = "Handicapped"
    else:
        category = "Regular"

    slot = (
        db.query(Slot)
        .filter(
            Slot.parking_lot_id == parking_lot.parking_lot_id,
            Slot.slot_category == category,
            Slot.is_occupied == False,
        )
        .first()
    )

    return slot
