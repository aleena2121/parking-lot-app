from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ParkingLotBase(BaseModel):
    capacity: int
    available_slots: List[str]
    is_full: bool

    model_config = ConfigDict(from_attributes=True)


class UpdateParkingLot(BaseModel):
    capacity: Optional[int] = None
    available_slots: Optional[List[str]] = None
    is_full: Optional[bool] = None

    model_config = ConfigDict(from_attributes=True)


class ShowParkingLot(ParkingLotBase):
    parking_lot_id: str
