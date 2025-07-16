from fastapi import APIRouter, Depends, status
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.config.logger_config import func_logger
from app.db.session import get_db
from app.enums.role_enum import RoleEnum
from app.exceptions import db_exceptions, parking_lot_exceptions, user_exceptions
from app.models.attendant_model import Attendant
from app.models.parking_lot_model import ParkingLot
from app.schemas.attendant_schema import UpdateAttendantLot
from app.schemas.response_schema import StandardResponse
from app.utils.role_checker import require_role

assign_lot_router = APIRouter(prefix="/assign-lot", tags=["Assign Lot"])


@assign_lot_router.put("/{user_id}")
def assign_lot_to_attendant(
    user_id: str,
    request: UpdateAttendantLot,
    db: Session = Depends(get_db),
    current_user=Depends(require_role(RoleEnum.ADMIN)),
):
    try:
        attendant = db.query(Attendant).filter(Attendant.user_id == user_id).first()
        if not attendant:
            raise user_exceptions.UserNotFound(user_id)
        
        lot = db.query(ParkingLot).filter(ParkingLot.parking_lot_id == request.alloted_lot).first()
        if not lot:
            raise parking_lot_exceptions.ParkingLotDoesNotExist()

        attendant.alloted_lot = request.alloted_lot

        db.commit()
        db.refresh(attendant)

        return StandardResponse(
            message="Lot Alloted successfully",
            payload={
                "user_id": attendant.user_id,
                "alloted_lot": attendant.alloted_lot,
            },
            status_code=status.HTTP_200_OK,
        )

    except SQLAlchemyError as e:
        db.rollback()
        func_logger.error(f"{e}")
        raise db_exceptions.DatabaseIntegrityError()
