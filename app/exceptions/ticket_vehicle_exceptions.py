from fastapi import HTTPException, status


class NoTicketFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Ticket Not Found.",
        )


class VehicleAlreadyExited(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Vehicle already exited.",
        )


class VehicleNotFound(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehicle not found.",
        )
