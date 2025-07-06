from fastapi import APIRouter, Depends, status
from app.db.session import get_db
from sqlalchemy.orm import Session
from app.models.attendant_model import Attendant
from app.auth.oauth2 import get_current_user
from app.enums.role_enum import RoleEnum
from app.config.logger_config import func_logger
from app.exceptions import auth_exceptions, db_exceptions, user_exceptions
from app.schemas.attendant_schema import UpdateAttendantLot
from app.schemas.response_schema import StandardResponse
from sqlalchemy.exc import SQLAlchemyError

assign_lot_router = APIRouter(prefix="/assign-lot", tags="Assign Lot")


def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != RoleEnum.ADMIN:
        func_logger.warning(
            f"Unauthorized update attempt by user {current_user.user_id}"
        )
        raise auth_exceptions.UnauthorizedAccess()
    return current_user


@assign_lot_router.put("/{user_id}")
def assign_lot_to_attendant(
    user_id: str,
    request: UpdateAttendantLot,
    db: Session = Depends(get_db),
    current_user=Depends(require_admin),
):
    try:
        attendant = db.query(Attendant).filter(Attendant.user_id == user_id).first()
        if not attendant:
            raise user_exceptions.UserNotFound(user_id)

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
