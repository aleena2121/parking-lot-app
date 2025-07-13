from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.enums.driver_enum import DriverEnum
from app.enums.vehicle_enum import VehicleEnum


class VehicleBase(BaseModel):
    plate_number: str
    make: str
    model: str
    color: str
    vehicle_category: VehicleEnum
    driver_category: DriverEnum
    driver_phone_no: str

    model_config = ConfigDict(from_attributes=True)


class ShowVehicle(VehicleBase):
    vehicle_id: str


class SearchVehicle(BaseModel):
    lot_id: str
    color: Optional[str]
    make: Optional[str]
    model: Optional[str]