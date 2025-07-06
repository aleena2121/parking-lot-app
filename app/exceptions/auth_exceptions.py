from fastapi import HTTPException, status

from app.config.logger_config import func_logger


class UnauthorizedAccess(HTTPException):
    def __init__(self, detail: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )


class CredentialsException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidCredentialsException(HTTPException):
    def __init__(self, email: str = None):
        detail = "Invalid credentials"
        if email:
            detail = f"Invalid credentials for user: {email}"
            func_logger.warning(detail)

        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenCreationError(HTTPException):
    def __init__(self, e: str):
        func_logger.error(f"Token creation failed: {e}")
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create authentication token",
        )
