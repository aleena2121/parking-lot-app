from fastapi import HTTPException, status


class ParkingLotFullException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Parking Lot full, check other lots",
        )


class NoLotFoundException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No empty lot found",
        )


class SlotsOccupiedException(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"Cannot reduce capacity, slots are occupied.",
        )

class ParkingLotDoesNotExist(HTTPException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_405_METHOD_NOT_ALLOWED,
            detail=f"Parking lot does not exist.",
        )