from fastapi import HTTPException, status


class ParkingLotFullException(HTTPException):
    def __init__(self, email: str):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parking Lot full, check other lots",
        )
