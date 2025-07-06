from fastapi import HTTPException, status


class UserAlreadyExists(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {email} already exists",
        )


class UserNotFound(HTTPException):
    def __init__(self, user_id: str = None):
        detail = "User not found"
        if user_id:
            detail = f"User with ID {user_id} not found"

        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )
