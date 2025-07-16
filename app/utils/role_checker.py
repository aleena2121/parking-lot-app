from fastapi.params import Depends

from app.auth.oauth2 import get_current_user
from app.config.logger_config import func_logger
from app.enums.role_enum import RoleEnum
from app.exceptions import auth_exceptions


def require_role(*allowed_roles: RoleEnum):
    def role_checker(current_user=Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            func_logger.warning(
                f"Unauthorized update attempt by user {current_user.user_id}"
            )
            raise auth_exceptions.UnauthorizedAccess()
        return current_user

    return role_checker
