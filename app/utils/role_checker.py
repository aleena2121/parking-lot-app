from fastapi.params import Depends

from app.auth.oauth2 import get_current_user
from app.config.logger_config import func_logger
from app.enums.role_enum import RoleEnum
from app.exceptions import auth_exceptions


def require_attendant(current_user=Depends(get_current_user)):
    if current_user.role != RoleEnum.ATTENDANT:
        func_logger.warning(
            f"Unauthorized update attempt by user {current_user.user_id}"
        )
        raise auth_exceptions.UnauthorizedAccess()
    return current_user


def require_admin(current_user=Depends(get_current_user)):
    if current_user.role != RoleEnum.ADMIN:
        func_logger.warning(
            f"Unauthorized update attempt by user {current_user.user_id}"
        )
        raise auth_exceptions.UnauthorizedAccess()
    return current_user
