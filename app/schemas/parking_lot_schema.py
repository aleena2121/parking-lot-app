from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class ParkingLotBase(BaseModel):
    capacity: int

    model_config = ConfigDict(from_attributes=True)


class UpdateParkingLot(BaseModel):
    capacity: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)


class ShowParkingLot(ParkingLotBase):
    parking_lot_id: str
    available_slots: List[str]
