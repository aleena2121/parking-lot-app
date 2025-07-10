from typing import List

from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.auth.oauth2 import get_current_user
from app.config.logger_config import func_logger
from app.db.session import get_db
from app.enums.role_enum import RoleEnum
from app.exceptions import auth_exceptions, db_exceptions
from app.models.parking_lot_model import ParkingLot
from app.queries.parking_lot_queries import get_all_lots, get_lot_by_id
from app.schemas.parking_lot_schema import (ParkingLotBase, ShowParkingLot,
                                            UpdateParkingLot)
from app.schemas.response_schema import StandardResponse
from app.services.parking_lot_services import (create_slots_and_row,
                                               update_slots_and_capacity)
from app.utils.role_checker import require_admin

parking_lot_router = APIRouter(prefix="/parking-lot", tags=["Parking Lot"])


@parking_lot_router.post("/", response_model=StandardResponse[ShowParkingLot])
def create_parking_lot(
    request: ParkingLotBase,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        parking_lot = ParkingLot(**request.model_dump(exclude_unset=True))
        db.add(parking_lot)
        db.flush()

        create_slots_and_row(request.capacity, db, parking_lot)
        db.commit()
        db.refresh(parking_lot)
        func_logger.info(f"Parking lot created, ID: {parking_lot.parking_lot_id}")

        return StandardResponse(
            message="New Parking Lot added",
            payload=parking_lot,
            status_code=status.HTTP_201_CREATED,
        )
    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"DB Error: {e}")
        raise db_exceptions.DatabaseIntegrityError(e)


@parking_lot_router.get("/", response_model=StandardResponse[List[ShowParkingLot]])
def get_all_parking_lots(
    db: Session = Depends(get_db), current_user=Depends(require_admin)
):
    lots = get_all_lots(db)
    func_logger.info(f"Returned {len(lots)} lots")
    return StandardResponse(
        message=f"{len(lots)} lots found", payload=lots, status_code=status.HTTP_200_OK
    )


@parking_lot_router.get("/{lot_id}", response_model=StandardResponse[ShowParkingLot])
def get_parking_lot_by_id(
    lot_id: str, db: Session = Depends(get_db), current_user=Depends(require_admin)
):
    lot = get_lot_by_id(db, lot_id)
    func_logger.info(f"Returned Parking lot, ID: {lot_id}")
    return StandardResponse(
        message="Parking lot retrieved", payload=lot, status_code=status.HTTP_200_OK
    )


@parking_lot_router.put("/{lot_id}", response_model=StandardResponse[ShowParkingLot])
def update_parking_lot(
    lot_id: str,
    request: UpdateParkingLot,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    lot = get_lot_by_id(db, lot_id)
    new_capacity = request.capacity

    try:
        update_slots_and_capacity(new_capacity, db, lot)
        return StandardResponse(
            message="Parking lot capacity updated",
            payload=lot,
            status_code=status.HTTP_200_OK,
        )
    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"{e}")
        raise db_exceptions.DatabaseIntegrityError(e)


@parking_lot_router.delete("/{lot_id}", response_model=StandardResponse[str])
def delete_parking_lot(
    lot_id: str, db: Session = Depends(get_db), current_user=Depends(require_admin)
):
    try:
        lot = get_lot_by_id(db, lot_id)
        db.delete(lot)
        db.commit()
        func_logger.info(f"Deleted parking lot ID: {lot_id}")
        return StandardResponse(
            message="Parking lot deleted",
            payload=lot_id,
            status_code=status.HTTP_200_OK,
        )
    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"Deletion Error: {e}")
        raise db_exceptions.DatabaseIntegrityError(e)
