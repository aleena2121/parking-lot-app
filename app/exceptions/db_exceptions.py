from fastapi import HTTPException, status

from app.config.logger_config import func_logger


class DatabaseIntegrityError(HTTPException):
    def __init__(self, e: str, detail: str = None):
        func_logger.error(f"Database integrity error: {e}")
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=detail or "Database operation failed due to integrity constraints",
        )
